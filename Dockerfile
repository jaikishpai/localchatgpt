FROM python:3.12.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Force CPU-only PyTorch installation
RUN pip install torch torchvision torchaudio --index-url https://pypi.org/simple/

# Copy Pipenv files first for caching
COPY Pipfile Pipfile.lock ./

# Install pipenv and dependencies
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile --system

# Copy the rest of the code
COPY . .

EXPOSE 8000

CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 