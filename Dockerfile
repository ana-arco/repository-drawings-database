FROM python:3.11-slim

# Install system dependencies needed for compiling the mariadb Python client
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application source code
COPY . .

# Set Flask environment variables
ENV FLASK_APP=app.py/app.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Expose port 5000 for local development server
EXPOSE 5000

# Start Flask development server
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
