FROM python:3.13.5-slim

# Set environment variables
ENV POETRY_VERSION=1.5.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock* /app/

# Install the dependencies
RUN poetry install --no-root

# Copy the application code to the container
COPY grabbit /app/grabbit

# Install the application
RUN poetry install --no-root

# Command to run the application
ENTRYPOINT ["poetry", "run", "grabbit"]

# Set the default command to run when starting the container
CMD ["--help"]
