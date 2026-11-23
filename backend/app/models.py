from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator

TrackId = Literal["use", "build"]
Level = Literal["beginner", "intermediate", "advanced"]
ResourceType = Literal["docs", "course", "video", "article", "tool", "repo"]
Cost = Literal["free", "paid"]

TAKEAWAY_MAX_WORDS = 12


def _check_takeaway(value: str) -> str:
    if len(value.split()) > TAKEAWAY_MAX_WORDS:
        raise ValueError(f"takeaway must be {TAKEAWAY_MAX_WORDS} words or fewer: {value!r}")
    return value


class Resource(BaseModel):
    id: str
    title: str
    url: HttpUrl
    provider: str
    type: ResourceType
    level: Level
    cost: Cost
    description: str


class Topic(BaseModel):
    title: str
    takeaway: str
    example: str = Field(min_length=1)

    _takeaway = field_validator("takeaway")(_check_takeaway)


class CodeSnippet(BaseModel):
    language: str = Field(min_length=1)
    content: str = Field(min_length=1)


class Example(BaseModel):
    title: str = Field(min_length=1)
    scenario: str = Field(min_length=1)
    steps: list[str] = Field(min_length=1)
    prompt: str | None = None
    code: CodeSnippet | None = None
    expected_result: str = Field(min_length=1)


class ExampleRef(BaseModel):
    title: str


class Track(BaseModel):
    id: TrackId
    order: int
    title: str
    description: str


class TrackSummary(BaseModel):
    id: TrackId
    title: str
    description: str
    stage_count: int


class StageBase(BaseModel):
    id: str
    track: TrackId
    order: int
    title: str
    summary: str
    takeaway: str
    icon: str | None = None
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    level: Level
    estimated_time: str
    topics: list[Topic]

    _takeaway = field_validator("takeaway")(_check_takeaway)


class StageSummary(StageBase):
    resource_count: int


class Stage(StageBase):
    goals: list[str]
    example: Example
    resources: list[Resource]


class Roadmap(BaseModel):
    version: str
    updated: str
    tracks: list[Track]
    stages: list[Stage]


class ResourceWithStage(Resource):
    track: TrackId
    stage_id: str
    stage_title: str


class MindmapStage(BaseModel):
    id: str
    title: str
    icon: str | None
    color: str
    takeaway: str
    example: ExampleRef
    topics: list[Topic]


class MindmapTrack(BaseModel):
    id: TrackId
    title: str
    description: str


class Mindmap(BaseModel):
    track: MindmapTrack
    stages: list[MindmapStage]
