FROM python:3.11.5 AS compile-image

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
  POETRY_VERSION=1.6.1


RUN printf "================\n\nStart build chat service. with USER: "${USER}"\n\n===============\n" \
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
    libffi-dev \
    cmake \
    libcurl4-openssl-dev \
  && pip install --upgrade pip \
  # Installing `poetry` package manager:
  && pip install poetry==$POETRY_VERSION wheel \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

USER "$USER"

RUN if [ "$USER" != "root" ]; then \
      mkdir /home/"$USER" \
      && groupadd -r "$USER" && useradd -d /home/"$USER" -r -g "$USER" "$USER" \
      && chown "$USER":"$USER" -R /home/"$USER"; \
    fi

COPY --chown="$USER":"$USER" ../poetry.lock ../pyproject.toml /app/

# Installing requirements
RUN poetry --version \
  && poetry run pip install -U pip \
  && poetry install $(if [ "$USER" != 'root' ]; then echo '--only main'; fi) --no-interaction --no-ansi \
  # Cleaning poetry installation's cache for production:
  && if [ "$USER" != 'root' ]; then rm -rf "$POETRY_CACHE_DIR"; fi


#==================== bot-service =================================
FROM compile-image as bot-service

USER "$USER"

COPY ./scripts/start-bot.sh /app/
RUN chmod +x ./start-bot.sh

# Copying bot service
COPY --chown="$USER":"$USER" ../bot_microservice /app/


#===================== chat-service ================================
FROM compile-image as chat-service

USER "$USER"

# Copying bot service
COPY --chown="$USER":"$USER" ../chat_gpt_microservice /app/

RUN chmod -R 777 translations

CMD ["python3", "./run.py"]