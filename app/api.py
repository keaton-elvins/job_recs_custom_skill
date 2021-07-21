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
import pandas as pd

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

    skills = set([ent.label_[6:] for ent in doc.ents if ent.label_.startswith("SKILL|")])
    job_recs = []

    df = pd.read_csv("search/Jobs.csv", encoding='cp1252')

    for i in df.index:
        score = 0
        reqs = eval(df.at[i, "Skills"])
        for s in reqs:
            if s in skills:
                score += 1
            
        if i < 10:
            row = df.loc[i]
            job_recs.append({"Name":row[0], "Link":row[1], "Score":score})
            weakest = min(job_recs, key=lambda rec: rec["Score"])

        elif score > weakest["Score"]:
            job_recs.remove(weakest)
            weakest = min(job_recs, key=lambda rec: rec["Score"])

            row = df.loc[i]
            job_recs.append({"Name":row[0], "Link":row[1], "Score":score})
            
    job_recs.reverse()

    res.update({"recordId": body.values[0].recordId})
    res.update({"data": {"skills": job_recs}})
      
    return {"values": [res]}
