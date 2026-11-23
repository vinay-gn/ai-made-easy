from functools import lru_cache
from pathlib import Path

from app.config import get_settings
from app.models import Cost, Level, ResourceType, ResourceWithStage, Roadmap, Stage, StageSummary


def load_roadmap(path: Path) -> Roadmap:
    roadmap = Roadmap.model_validate_json(path.read_text(encoding="utf-8"))
    _check_unique_ids(roadmap)
    roadmap.stages.sort(key=lambda s: s.order)
    return roadmap


def _check_unique_ids(roadmap: Roadmap) -> None:
    stage_ids = [s.id for s in roadmap.stages]
    resource_ids = [r.id for s in roadmap.stages for r in s.resources]
    for kind, ids in (("stage", stage_ids), ("resource", resource_ids)):
        duplicates = {i for i in ids if ids.count(i) > 1}
        if duplicates:
            raise ValueError(f"Duplicate {kind} ids in roadmap data: {sorted(duplicates)}")


@lru_cache
def get_roadmap() -> Roadmap:
    return load_roadmap(get_settings().data_file_path)


class RoadmapService:
    def __init__(self, roadmap: Roadmap):
        self._roadmap = roadmap

    def list_stages(self) -> list[StageSummary]:
        return [
            StageSummary(
                **s.model_dump(exclude={"goals", "resources"}),
                resource_count=len(s.resources),
            )
            for s in self._roadmap.stages
        ]

    def get_stage(self, stage_id: str) -> Stage | None:
        return next((s for s in self._roadmap.stages if s.id == stage_id), None)

    def search_resources(
        self,
        level: Level | None = None,
        type: ResourceType | None = None,
        cost: Cost | None = None,
        q: str | None = None,
    ) -> list[ResourceWithStage]:
        needle = q.strip().lower() if q else ""
        results = []
        for stage in self._roadmap.stages:
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
                    ResourceWithStage(**r.model_dump(), stage_id=stage.id, stage_title=stage.title)
                )
        return results


def get_roadmap_service() -> RoadmapService:
    return RoadmapService(get_roadmap())
