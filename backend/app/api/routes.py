from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.exceptions import RequestValidationError

from app.models import (
    Cost,
    Level,
    Mindmap,
    ResourceType,
    ResourceWithStage,
    Stage,
    StageSummary,
    TrackSummary,
)
from app.services.roadmap import RoadmapService, get_roadmap_service

router = APIRouter()

Service = Annotated[RoadmapService, Depends(get_roadmap_service)]


def _enabled_track(
    service: Service,
    track: Annotated[str | None, Query(description="Track id; must be one of the enabled tracks (see /api/tracks).")] = None,
) -> str | None:
    """Unknown and disabled tracks are both rejected with the standard 422 validation error."""
    if track is None or track in service.track_ids:
        return track
    quoted = [f"'{t}'" for t in service.track_ids]
    expected = quoted[0] if len(quoted) == 1 else f"{', '.join(quoted[:-1])} or {quoted[-1]}"
    raise RequestValidationError(
        [
            {
                "type": "literal_error",
                "loc": ("query", "track"),
                "msg": f"Input should be {expected}",
                "input": track,
                "ctx": {"expected": expected},
            }
        ]
    )


EnabledTrack = Annotated[str | None, Depends(_enabled_track)]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/tracks", response_model=list[TrackSummary])
def list_tracks(service: Service):
    return service.list_tracks()


@router.get("/tracks/{track_id}/mindmap", response_model=Mindmap)
def get_mindmap(track_id: str, service: Service):
    # A track in the path is a resource: unknown and disabled tracks are both 404.
    mindmap = service.get_mindmap(track_id)
    if mindmap is None:
        raise HTTPException(status_code=404, detail=f"Track '{track_id}' not found")
    return mindmap


@router.get("/stages", response_model=list[StageSummary])
def list_stages(service: Service, track: EnabledTrack):
    return service.list_stages(track=track)


@router.get("/stages/{stage_id}", response_model=Stage)
def get_stage(stage_id: str, service: Service):
    stage = service.get_stage(stage_id)
    if stage is None:
        raise HTTPException(status_code=404, detail=f"Stage '{stage_id}' not found")
    return stage


@router.get("/resources", response_model=list[ResourceWithStage])
def list_resources(
    service: Service,
    track: EnabledTrack,
    level: Level | None = None,
    type: ResourceType | None = None,
    cost: Cost | None = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
):
    return service.search_resources(track=track, level=level, type=type, cost=cost, q=q)
