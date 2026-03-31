# Use a lightweight official Python 3.11 image.
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies securely without cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the codebase into the container
COPY . .

# Expose the explicitly assigned interface
EXPOSE 8080

# Command to run on container start. We bind to 0.0.0.0 and port 8080, which Cloud Run natively expects.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
