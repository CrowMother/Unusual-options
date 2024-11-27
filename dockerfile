FROM python:3.11-slim

# Set the timezone environment variable (adjust to your desired timezone)
ENV TZ=America/New_York

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Set the default command to run your application
CMD ["python", "main.py"]