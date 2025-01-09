FROM python:3.8-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the service
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]