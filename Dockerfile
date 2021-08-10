FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

EXPOSE 80

COPY ./app /app

CMD ["python", "-m","uvicorn","main:app","--host","0.0.0.0","--port","80"]
