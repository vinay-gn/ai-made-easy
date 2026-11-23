from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path

from app.config import get_settings
from app.models import (
    Cost,
    Level,
    Mindmap,
    MindmapStage,
    MindmapTrack,
    ResourceType,
    ResourceWithStage,
    Roadmap,
    Stage,
    StageSummary,
    TrackId,
    TrackSummary,
)


def load_roadmap(path: Path) -> Roadmap:
    roadmap = Roadmap.model_validate_json(path.read_text(encoding="utf-8"))
    _check_integrity(roadmap)
    roadmap.tracks.sort(key=lambda t: t.order)
    track_order = {t.id: t.order for t in roadmap.tracks}
    roadmap.stages.sort(key=lambda s: (track_order[s.track], s.order))
    return roadmap


def _duplicates(ids: list) -> list:
    return sorted({i for i in ids if ids.count(i) > 1})


def _check_integrity(roadmap: Roadmap) -> None:
    checks = {
        "track": [t.id for t in roadmap.tracks],
        "stage": [s.id for s in roadmap.stages],
        "resource": [r.id for s in roadmap.stages for r in s.resources],
        "(track, order)": [(s.track, s.order) for s in roadmap.stages],
    }
    for kind, ids in checks.items():
        if dupes := _duplicates(ids):
            raise ValueError(f"Duplicate {kind} ids in roadmap data: {dupes}")
    known_tracks = {t.id for t in roadmap.tracks}
    if unknown := sorted({s.track for s in roadmap.stages} - known_tracks):
        raise ValueError(f"Stages reference undefined tracks: {unknown}")


@lru_cache
def get_roadmap() -> Roadmap:
    return load_roadmap(get_settings().data_file_path)


class RoadmapService:
    """Read access to the roadmap, limited to `enabled_tracks` (all tracks when None)."""

    def __init__(self, roadmap: Roadmap, enabled_tracks: Iterable[str] | None = None):
        enabled = set(enabled_tracks) if enabled_tracks is not None else {t.id for t in roadmap.tracks}
        self._tracks = [t for t in roadmap.tracks if t.id in enabled]
        self._all_stages = [s for s in roadmap.stages if s.track in enabled]

    @property
    def track_ids(self) -> list[str]:
        return [t.id for t in self._tracks]

    def _stages(self, track: TrackId | None) -> list[Stage]:
        return [s for s in self._all_stages if track is None or s.track == track]

    def list_tracks(self) -> list[TrackSummary]:
        return [
            TrackSummary(
                id=t.id,
                title=t.title,
                description=t.description,
                stage_count=len(self._stages(t.id)),
            )
            for t in self._tracks
        ]

    def get_mindmap(self, track_id: TrackId) -> Mindmap | None:
        track = next((t for t in self._tracks if t.id == track_id), None)
        if track is None:
            return None
        return Mindmap(
            track=MindmapTrack(**track.model_dump(include={"id", "title", "description"})),
            stages=[
                MindmapStage(
                    **s.model_dump(include={"id", "title", "icon", "color", "takeaway", "topics"}),
                    example={"title": s.example.title},
                )
                for s in self._stages(track_id)
            ],
        )

    def list_stages(self, track: TrackId | None = None) -> list[StageSummary]:
        return [
            StageSummary(
                **s.model_dump(exclude={"goals", "example", "resources"}),
                resource_count=len(s.resources),
            )
            for s in self._stages(track)
        ]

    def get_stage(self, stage_id: str) -> Stage | None:
        return next((s for s in self._all_stages if s.id == stage_id), None)

    def search_resources(
        self,
        track: TrackId | None = None,
        level: Level | None = None,
        type: ResourceType | None = None,
        cost: Cost | None = None,
        q: str | None = None,
    ) -> list[ResourceWithStage]:
        needle = q.strip().lower() if q else ""
        results = []
        for stage in self._stages(track):
            for r in stage.resources:
                if level and r.level != level:
                    continue
                if type and r.type != type:
                    continue
                if cost and r.cost != cost:
                    continue
                if needle and needle not in f"{r.title} {r.description} {r.provider}".lower():
                    continue
                results.append(
                    ResourceWithStage(
                        **r.model_dump(), track=stage.track, stage_id=stage.id, stage_title=stage.title
                    )
                )
        return results


def get_roadmap_service() -> RoadmapService:
    return RoadmapService(get_roadmap(), get_settings().enabled_track_list)
