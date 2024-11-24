# Official Python image
FROM python:3.9-slim

# Set working directory to /app to execute following commands
WORKDIR /app

# Copy contents of /app to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port accessible 
EXPOSE 8080

# Define environment variable
ENV FLASK_APP=app.py

# Command to run the application when the container starts
CMD ["flask", "run", "--host=0.0.0.0"]

