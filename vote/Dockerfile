# 1. Start from a lightweight Linux environment with Python pre-installed
FROM python:3.11-slim

# 2. Set the internal working directory inside the container
WORKDIR /app

# 3. Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# 4. Install the Python dependencies (Flask and Redis)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code into the container
COPY . .

# 6. Document that this container listens on port 5000
EXPOSE 5000

# 7. Define the default command to run when the container starts
CMD ["python", "app.py"]
