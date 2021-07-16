# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Dict, List, Optional
from pydantic import BaseModel


ENT_PROP_MAP = {
    "CARDINAL": "cardinals",
    "DATE": "dates",
    "EVENT": "events",
    "FAC": "facilities",
    "GPE": "gpes",
    "LANGUAGE": "languages",
    "LAW": "laws",
    "LOC": "locations",
    "MONEY": "money",
    "NORP": "norps",
    "ORDINAL": "ordinals",
    "ORG": "organizations",
    "PERCENT": "percentages",
    "PERSON": "people",
    "PRODUCT": "products",
    "QUANTITY": "quanities",
    "TIME": "times",
    "WORK_OF_ART": "worksOfArt",
}


class RecordDataRequest(BaseModel):
    text: str


class RecordRequest(BaseModel):
    recordId: str
    data: RecordDataRequest


class RecordsRequest(BaseModel):
    values: List[RecordRequest]


class RecordDataResponse(BaseModel):
    skills: List


class Message(BaseModel):
    message: str


class RecordResponse(BaseModel):
    recordId: str
    data: RecordDataResponse


class RecordsResponse(BaseModel):
    values: List[RecordResponse]


class RecordEntitiesByTypeResponse(BaseModel):
    recordId: str
    data: Dict[str, List[str]]


class RecordsEntitiesByTypeResponse(BaseModel):
    values: List[RecordEntitiesByTypeResponse]
