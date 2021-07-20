import requests
from bs4 import BeautifulSoup
import csv

import spacy
from spacy import EntityRuler

URL = "https://www.indeed.com"

nlp = spacy.load("en_core_web_sm")
ruler = EntityRuler(nlp, overwrite_ents=True).from_disk("app/data/patterns.jsonl")

with open('search/Jobs.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        link = URL + row["Link"]
        page = requests.get(link)

        soup = BeautifulSoup(page.content, "html.parser")
        description = soup.find(id='jobDescriptionText')

        text_chunks = description.find_all(text=True)
        text = " ".join(text_chunks).strip('\n')
        
        break
