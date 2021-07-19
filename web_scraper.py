import requests
from bs4 import BeautifulSoup

URL = "https://www.indeed.com/jobs?q=software+engineer&limit=50&start="

jobs_list = {}

titles, links = [], []

for i in range(0, 200, 50):
    page = requests.get(URL + str(i))

    soup = BeautifulSoup(page.content, "html.parser")
    job_soup = soup.find(id="mosaic-provider-jobcards")

    job_results = job_soup.find_all('a', class_="tapItem")

    for result in job_results:
        links += [result.get('href')]
        titles += [result.find("h2", class_='jobTitle').text]

titles = list(set(titles))
links = list(set(links))
    
jobs_list.update({"titles":titles})
jobs_list.update({"links":links})

print(jobs_list["titles"])