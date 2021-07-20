import requests
from bs4 import BeautifulSoup
import csv

URL = "https://www.indeed.com/jobs?q=software+engineer&limit=50&start="

jobs_list = []

for i in range(0, 500, 50):
    page = requests.get(URL + str(i))

    soup = BeautifulSoup(page.content, "html.parser")
    job_soup = soup.find(id="mosaic-provider-jobcards")

    job_results = job_soup.find_all('a', class_="tapItem")

    for result in job_results:
        job_entry = {}
        job_entry.update({"Title": result.find("h2", class_='jobTitle').text.strip()})
        job_entry.update({"Link": result.get('href').strip()})

        if not job_entry["Link"].startswith("/pagead"):
            jobs_list.append(job_entry)

csv_file = "search/Jobs.csv"
try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Title", "Link"])
        writer.writeheader()
        for data in jobs_list:
            try:
                writer.writerow(data)
            except UnicodeEncodeError:
                continue
except IOError:
    print("I/O error")