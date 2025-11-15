FROM python:3.11-slim

WORKDIR /app

# Install runtime deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn

# Copy application
COPY . /app

ENV FLASK_ENV=production
EXPOSE 5000

# Use gunicorn to run the Flask app (single worker is fine for demo)
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "cssa_agent:app"]
