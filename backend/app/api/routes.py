from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models import Cost, Level, ResourceType, ResourceWithStage, Stage, StageSummary
from app.services.roadmap import RoadmapService, get_roadmap_service

router = APIRouter()

Service = Annotated[RoadmapService, Depends(get_roadmap_service)]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/stages", response_model=list[StageSummary])
def list_stages(service: Service):
    return service.list_stages()


@router.get("/stages/{stage_id}", response_model=Stage)
def get_stage(stage_id: str, service: Service):
    stage = service.get_stage(stage_id)
    if stage is None:
        raise HTTPException(status_code=404, detail=f"Stage '{stage_id}' not found")
    return stage


@router.get("/resources", response_model=list[ResourceWithStage])
def list_resources(
    service: Service,
    level: Level | None = None,
    type: ResourceType | None = None,
    cost: Cost | None = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
):
    return service.search_resources(level=level, type=type, cost=cost, q=q)
