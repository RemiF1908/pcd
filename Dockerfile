FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt -i https://pypi.org/simple

COPY src/ ./src/
COPY campaign.json .

EXPOSE 8000

CMD ["python", "-m", "src.main", "--web"]
