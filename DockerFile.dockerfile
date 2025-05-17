# Use an official Python runtime as a parent image
# Using python:3.10-slim as a good balance of features and size.
# Ensure this matches the Python version you've been developing with if there are specific version dependencies.
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
# This is done first to leverage Docker's layer caching if requirements don't change often.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir reduces image size by not storing the pip download cache
# --upgrade pip ensures the latest pip is used for installations
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the entire project (except for what's in .dockerignore) into the container at /app
# This includes your app.py, rag_agent/ folder, templates/, static/, etc.
COPY . .

# Make port 5000 available to the world outside this container
# This is the port your Flask app runs on (as defined in app.py)
EXPOSE 5000

# Define environment variables for Flask
# These can be overridden at runtime if needed
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
# Setting PYTHONUNBUFFERED to 1 ensures that Python output (e.g., print statements, logs)
# is sent straight to the terminal without being buffered, which is good for debugging.
ENV PYTHONUNBUFFERED=1

# Command to run the application
# Flask will find app.py due to FLASK_APP env var and the WORKDIR.
# The host and port are set within your app.py's app.run() command.
CMD ["flask", "run"]