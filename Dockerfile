FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary

COPY . .

# Make the wait script executable
COPY wait_for_db.py .
RUN chmod +x wait_for_db.py

EXPOSE 8000

# Wait for database before starting the app
CMD ["sh", "-c", "python wait_for_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]