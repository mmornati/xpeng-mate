# Use a slim Python image
FROM python:3.11-slim

# Set workdir
WORKDIR /

# Copy files
COPY /app/requirements.txt .
COPY /app/main.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the script
CMD ["python", "main.py"]