from collections import defaultdict
import os

from fastapi import FastAPI, Body
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import spacy
import srsly
import pandas as pd

from models import (
    ENT_PROP_MAP,
    RecordsRequest,
    RecordsResponse,
)
from spacy.pipeline import EntityRuler


app = FastAPI(
    title="job_recs_custom_skill",
    version="1.0",
    description="Azure Search Cognitive Skill to recommend job openings based on extracted technical/business skills from text",
)

example_request = srsly.read_json("data/example_request.json")

nlp = spacy.load("en_core_web_sm")
ruler = EntityRuler(nlp, overwrite_ents=True).from_disk("data/patterns.jsonl")

def get_score(skills, reqs):
    """Given a list of job requirements, evaluate score based on user's skills"""
    #TODO: improve scoring algorithm
    score = 0
    for s in reqs:
            if s in skills:
                score += 1

    return score

@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse("docs")


@app.post("/recs", response_model=RecordsResponse, tags=["NER"])
async def find_recs(body: RecordsRequest = Body(..., example=example_request)):
    """Find job recs given skills extracted from body of text."""
    
    res = {}

    raw_body = body.values[0].data.text
    doc = ruler(nlp(raw_body))

    skills = set([ent.label_[6:] for ent in doc.ents if ent.label_.startswith("SKILL|")])
    job_recs = []

    df = pd.read_csv("data/Jobs.csv", encoding='cp1252')

    # find top 10 jobs with highest score
    for i in df.index:
        score = 0
        reqs = eval(df.at[i, "Skills"])
        score = get_score(skills, reqs)
            
        if i < 10:
            row = df.loc[i]
            job_recs.append({"Name":row[0], "Link":row[1], "Score":score})
            weakest = min(job_recs, key=lambda rec: rec["Score"])

        elif score > weakest["Score"]:
            job_recs.remove(weakest)

            row = df.loc[i]
            job_recs.append({"Name": row[0], "Link": row[1], "Score": score})

            weakest = min(job_recs, key=lambda rec: rec["Score"])

    job_recs.reverse()

    res.update({"recordId": body.values[0].recordId})
    res.update({"data": {"skills": job_recs}})
      
    return {"values": [res]}
