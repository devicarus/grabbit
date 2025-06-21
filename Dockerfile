FROM python:3.13.5-slim

# Set environment variables
ENV POETRY_VERSION=2.1.3 \
    POETRY_NO_INTERACTION=1 \
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

# Copy the application code and README to the container
COPY grabbit /app/grabbit
COPY README.md /app/

# Install the application
RUN poetry install

# Command to run the application
ENTRYPOINT ["poetry", "run", "grabbit"]

# Set the default command to run when starting the container
CMD ["--help"]
