FROM python:3.11.3-slim-buster

RUN pip install poetry

RUN mkdir /src
WORKDIR /src

COPY . /src

RUN poetry config virtualenvs.create true && poetry install --no-interaction --no-ansi --without dev

USER 1000
EXPOSE 8050
CMD ["python", "src/ai_leads/ui/dash_app/index.py"]