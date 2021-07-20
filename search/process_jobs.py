import requests
from bs4 import BeautifulSoup
import csv
from requests.api import get
import spacy
from spacy.pipeline import EntityRuler

def get_skills(link=str):
    page = requests.get(link)

    soup = BeautifulSoup(page.content, "html.parser")
    description = soup.find(id='jobDescriptionText')

    text_chunks = description.find_all(text=True)
    
    text = " ".join(text_chunks).strip('\n')

    doc = ruler(nlp(text))

    skills = set([ent.label_[6:] for ent in doc.ents if ent.label_.startswith("SKILL|")])

    return skills


nlp = spacy.load("en_core_web_sm")
ruler = EntityRuler(nlp, overwrite_ents=True).from_disk("app/data/patterns.jsonl")

URL = "https://www.indeed.com/jobs?q=software+engineer&limit=50&start="

jobs_list = []

for i in range(0, 500, 50):
    page = requests.get(URL + str(i))

    soup = BeautifulSoup(page.content, "html.parser")
    job_soup = soup.find(id="mosaic-provider-jobcards")

    job_results = job_soup.find_all('a', class_="tapItem")

    for result in job_results:
        link = "https://www.indeed.com" + result.get('href').strip()
        
        if not link.startswith("/pagead"):
            job_entry = {}
            job_entry.update({"Title": result.find("h2", class_='jobTitle').text.strip()})
            job_entry.update({"Link": link})
            job_entry.update({"Skills": get_skills(link)})
            jobs_list.append(job_entry)
                

csv_file = "search/Jobs.csv"
try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Title", "Link", "Skills"])
        writer.writeheader()
        for data in jobs_list:
            try:
                writer.writerow(data)
            except UnicodeEncodeError:
                continue
except IOError:
    print("I/O error")


