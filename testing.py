from collections import defaultdict
import os

from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Body
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import spacy
import pandas as pd
from spacy.pipeline import EntityRuler

nlp = spacy.load("en_core_web_sm")
ruler = EntityRuler(nlp, overwrite_ents=True).from_disk("app/data/patterns.jsonl")

res = {}

raw_body = "Experience with OOP using Python and Java. Familiar with NumPy and Pandas libraries and comfortable working in a Linux environment."
doc = ruler(nlp(raw_body))

skills = set([ent.label_[6:] for ent in doc.ents if ent.label_.startswith("SKILL|")])
job_recs = []

df = pd.read_csv("search/Jobs.csv", encoding='cp1252')
threshold = 0
row = {}
for i in df.index:
    score = 0
    reqs = eval(df.at[i, "Skills"])
    
    for s in reqs:
        if s in skills:
            score += 1

    if score > threshold:
        threshold = score
        row = df.loc[i]
        print(row[0], row[1])

res.update({"recordId": "a1"})
res.update({"data": {"skills": [row]}})

