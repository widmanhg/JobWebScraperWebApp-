# Use an official Python base image
FROM python:3.11.8-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables for Flask
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0

# Copy the requirements.txt file and the source code to the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Command to run the Flask application
CMD ["flask", "run"]
