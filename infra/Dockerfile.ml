FROM python:3.11-slim

WORKDIR /app

COPY services/ml/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/ml/ .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

EXPOSE 8010

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010", "--reload"]
