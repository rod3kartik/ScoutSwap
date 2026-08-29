"""Typed models for the football-data.org responses ScoutSwap uses."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class Contract(ApiModel):
    start: Optional[str] = None
    until: Optional[str] = None


class Player(ApiModel):
    id: int
    name: str
    first_name: Optional[str] = Field(default=None, alias="firstName")
    last_name: Optional[str] = Field(default=None, alias="lastName")
    position: Optional[str] = None
    date_of_birth: Optional[date] = Field(default=None, alias="dateOfBirth")
    nationality: Optional[str] = None
    shirt_number: Optional[int] = Field(default=None, alias="shirtNumber")
    market_value: Optional[int] = Field(default=None, alias="marketValue")
    contract: Optional[Contract] = None


class Team(ApiModel):
    id: int
    name: str
    short_name: Optional[str] = Field(default=None, alias="shortName")
    tla: Optional[str] = None
    crest: Optional[str] = None
    market_value: Optional[int] = Field(default=None, alias="marketValue")
    squad: List[Player] = Field(default_factory=list)


class Competition(ApiModel):
    id: int
    name: str
    code: str


class CompetitionTeams(ApiModel):
    count: int
    competition: Competition
    teams: List[Team]
