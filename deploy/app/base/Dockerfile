FROM python:3.10

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/usr/src

RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg2 dependencies
  libpq-dev \
  # curl
  curl


# tzdata for timzone
RUN apt-get update -y
RUN apt-get install -y tzdata

# timezone env with default
ENV TZ=Europe/Kiev

# Upgrade pip
RUN pip install --upgrade pip
RUN pip install setuptools

WORKDIR $PYTHONPATH

COPY ./poetry.lock ./
COPY ./pyproject.toml ./

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH "/root/.local/bin:$PATH"


RUN poetry config virtualenvs.in-project true --local
RUN poetry install --no-root --only main --no-interaction --no-ansi

#WORKDIR /usr/src
COPY . /usr/src
COPY Makefile /usr/src/Makefile
