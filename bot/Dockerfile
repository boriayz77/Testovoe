FROM python:3.11-slim
RUN apt-get update && apt-get install -y build-essential libpq-dev libffi-dev python3-dev tzdata file
WORKDIR /bot
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt && chmod 755 .
COPY . .
CMD ["python3", "-u", "main.py"]