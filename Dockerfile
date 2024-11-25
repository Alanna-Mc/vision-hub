# Official Python image
FROM python:3.9-slim

# Set working directory to /app to execute following commands
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy contents of the application to the container
COPY . .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Set environment variables
ENV FLASK_APP=visionHub.py

# Expose the port your app runs on
EXPOSE 8080

# Set the entrypoint to your script
ENTRYPOINT ["./entrypoint.sh"]

# Command to run the application
CMD ["python", "visionHub.py"]
