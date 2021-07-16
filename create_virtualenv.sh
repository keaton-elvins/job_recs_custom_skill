pip3 install --user virtualenv
virtualenv .venv && source .venv/Scripts/activate && pip install -r ./requirements/base.txt && python -m spacy download en_core_web_sm