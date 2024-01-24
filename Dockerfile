FROM python:3.11-slim as build

# Update packages

RUN apt-get update \
    && apt-get install -y \
         curl \
         build-essential \
         libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
ENV POETRY_VERSION=1.5.0
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH /root/.local/bin:$PATH

# Set up venv
RUN python -m venv --copies /venv
COPY pyproject.toml poetry.lock ./
RUN . /venv/bin/activate && poetry install --only main

# Deploy image
FROM python:3.11-slim as deploy

# Update packages
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /venv /venv
ENV PATH /venv/bin:$PATH

# Add source
COPY . .

HEALTHCHECK --start-period=30s CMD curl localhost:8000/health

# Run uvicorn
CMD ["uvicorn", "lab4.main:app", "--host", "0.0.0.0"]

