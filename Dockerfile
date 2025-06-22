FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    python3-dev \
    tzdata \
    file \
    && apt-get clean

WORKDIR .

COPY bot/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY bot .

RUN chmod -R 755 .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/bot

CMD ["python3", "main.py"]
