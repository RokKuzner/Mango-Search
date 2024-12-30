# Use the official Python image as the base
FROM python:3.12

# Set environment variables to avoid interactive issues during installations
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code into the container
COPY . /app
WORKDIR /app

# Start the crawler
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]