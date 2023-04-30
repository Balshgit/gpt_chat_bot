FROM python:3.11.3

ARG USER

ENV USER=${USER} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  PATH="$PATH:/root/.poetry/bin" \
  DOCKER_CONTAINER=1 \
  POETRY_VERSION=1.4.2


RUN printf "================\n\nStart build app. USER is: "${USER}"\n\n===============\n" \
  && apt-get update \
  && apt-get install --no-install-recommends -y \
    bash \
    build-essential \
    curl \
    iputils-ping \
    gettext \
    git \
    libpq-dev \
    nano \
  && pip install --upgrade pip \
  # Installing `poetry` package manager:
  && pip install poetry==$POETRY_VERSION wheel \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*


WORKDIR /app

RUN if [ "$USER" != "root" ]; then \
      mkdir /home/"$USER" \
      && groupadd -r "$USER" && useradd -d /home/"$USER" -r -g "$USER" "$USER" \
      && chown "$USER":"$USER" -R /home/"$USER"; \
    fi

COPY --chown="$USER":"$USER" ./poetry.lock ./pyproject.toml /app/

# Installing requirements
RUN poetry --version \
  && poetry run pip install -U pip \
  && poetry install \
    $(if [ "$USER" != 'root' ]; then echo '--only main'; fi) \
    --no-interaction --no-ansi \
  # Cleaning poetry installation's cache for production:
  && if [ "$USER" != 'root' ]; then rm -rf "$POETRY_CACHE_DIR"; fi

COPY --chown="$USER":"$USER" ./app /app/
COPY ./scripts/start-bot.sh .
RUN chmod +x ./start-bot.sh

USER "$USER"

# Copying actuall application
COPY --chown="$USER":"$USER" . /app/
