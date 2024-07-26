# Use an official Python base image
FROM python:3.11.8-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables for Flask
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Add Google Chrome repository and key
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'

# Install Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

# Copy the requirements.txt file and the source code to the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Command to run the Flask application
CMD ["flask", "run"]