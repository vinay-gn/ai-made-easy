from typing import Literal

from pydantic import BaseModel, HttpUrl

Level = Literal["beginner", "intermediate", "advanced"]
ResourceType = Literal["docs", "course", "video", "article", "tool", "repo"]
Cost = Literal["free", "paid"]


class Resource(BaseModel):
    id: str
    title: str
    url: HttpUrl
    provider: str
    type: ResourceType
    level: Level
    cost: Cost
    description: str


class StageSummary(BaseModel):
    id: str
    order: int
    title: str
    summary: str
    level: Level
    estimated_time: str
    topics: list[str]
    resource_count: int


class Stage(BaseModel):
    id: str
    order: int
    title: str
    summary: str
    level: Level
    estimated_time: str
    goals: list[str]
    topics: list[str]
    resources: list[Resource]


class Roadmap(BaseModel):
    version: str
    updated: str
    stages: list[Stage]


class ResourceWithStage(Resource):
    stage_id: str
    stage_title: str
