# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from collections import defaultdict
import os

from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Body
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import spacy
import srsly
import uvicorn

from app.models import (
    ENT_PROP_MAP,
    RecordsRequest,
    RecordsResponse,
    RecordsEntitiesByTypeResponse,
)
from app.spacy_extractor import SpacyExtractor
from spacy.pipeline import EntityRuler


load_dotenv(find_dotenv())
prefix = os.getenv("CLUSTER_ROUTE_PREFIX", "").rstrip("/")


app = FastAPI(
    title="job_recs_custom_skill",
    version="1.0",
    description="Azure Search Cognitive Skill to recommend job openings based on extracted technical/business skills from text",
    openapi_prefix=prefix,
)

example_request = srsly.read_json("app/data/example_request.json")

nlp = spacy.load("en_core_web_sm")
extractor = SpacyExtractor(nlp)
ruler = EntityRuler(nlp, overwrite_ents=True).from_disk("app/data/patterns.jsonl")


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(f"{prefix}/docs")


@app.post("/entities", response_model=RecordsResponse, tags=["NER"])
async def extract_entities(body: RecordsRequest = Body(..., example=example_request)):
    """Extract Named Entities from a batch of Records."""
    
    res = {}

    raw_body = body.values[0].data.text
    doc = ruler(nlp(raw_body))

    res.update({"recordId": body.values[0].recordId})
    res.update({"data": {"entities": [{ent.label_: ent.text} for ent in doc.ents]}})
    res.update({"errors": [{"message": "None"}]})
    res.update({"warnings": [{"message": "None"}]})
      
    return {"values": [res]}


@app.post(
    "/entities_by_type", response_model=RecordsEntitiesByTypeResponse, tags=["NER"]
)
async def extract_entities_by_type(body: RecordsRequest = Body(..., example=example_request)):
    """Extract Named Entities from a batch of Records separated by entity label.
        This route can be used directly as a Cognitive Skill in Azure Search."""

    res = []
    documents = []

    for val in body.values:
        documents.append({"id": val.recordId, "text": val.data.text})

    entities_res = extractor.extract_entities(documents)
    res = []

    for er in entities_res:
        groupby = defaultdict(list)
        for ent in er["entities"]:
            ent_prop = ENT_PROP_MAP[ent["label"]]
            groupby[ent_prop].append(ent["name"])
        record = {"recordId": er["id"], "data": groupby}
        res.append(record)

    return {"values": res}
