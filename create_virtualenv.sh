pip3 install --user virtualenv
virtualenv .venv && source .venv/bin/activate && pip install -r ./requirements.txt && python -m spacy download en_core_web_sm