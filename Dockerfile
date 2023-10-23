FROM python:3.11

WORKDIR /app

COPY ./ ./

RUN apt-get update \
    && apt install libcairo2 libffi-dev \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install

CMD ["start_bot"]