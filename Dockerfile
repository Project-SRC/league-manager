FROM tiangolo/uvicorn-gunicorn:python3.8

LABEL maintainer="João Pedro Sconetto <sconetto.joao@gmail.com>"

RUN pip install --upgrade pip

RUN pip install --no-cache-dir fastapi pipenv

COPY Pipfile* /tmp/

RUN cd /tmp && pipenv lock --python $(which python) --requirements > requirements.txt

RUN pip install -r /tmp/requirements.txt --no-cache-dir

COPY src/ src/

COPY .env.example .env

RUN export PYTHONPATH=$(pwd)

CMD ["uvicorn", "src.main:league", "--host", "0.0.0.0", "--port", "80"]
