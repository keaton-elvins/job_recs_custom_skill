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
)
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
ruler = EntityRuler(nlp, overwrite_ents=True).from_disk("app/data/patterns.jsonl")


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(f"{prefix}/docs")


@app.post("/skills", response_model=RecordsResponse, tags=["NER"])
async def extract_skills(body: RecordsRequest = Body(..., example=example_request)):
    """Extract Named Skills from a batch of Records."""
    
    res = {}

    raw_body = body.values[0].data.text
    doc = ruler(nlp(raw_body))

    res.update({"recordId": body.values[0].recordId})
    res.update({"data": {"skills": [ent.label_[6:] for ent in doc.ents if ent.label_.startswith("SKILL|")]}})
      
    return {"values": [res]}