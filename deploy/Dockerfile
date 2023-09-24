FROM python:3.11.5 AS compile-image

ARG USER

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    DOCKER_CONTAINER=1 \
    POETRY_VERSION=1.6.1

RUN printf "================ Start build base service. with USER: ${USER} ===============" \
  && apt-get update \
  && apt-get install --no-install-recommends -y \
    bash \
    build-essential \
    iputils-ping \
    libpq-dev \
    libffi-dev \
    cmake \
    libcurl4-openssl-dev \
    bash \
    curl \
    git \
    nano \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app/

RUN if [ "$USER" != "root" ]; then \
      mkdir /home/"$USER" \
      && groupadd -r "$USER" && useradd -d /home/"$USER" -r -g "$USER" "$USER" \
      && chown "$USER":"$USER" -R /home/"$USER"; \
    fi

COPY --chown=${USER}:${USER} ../poetry.lock ../pyproject.toml /app/

RUN pip install --upgrade pip && pip install poetry==$POETRY_VERSION
RUN poetry config virtualenvs.in-project true && \
    poetry config virtualenvs.create true && \
    poetry install --only main --no-interaction --no-ansi && \
    rm -rf $POETRY_CACHE_DIR


#==================== bot-service =================================
FROM compile-image as bot-service

RUN printf "================ Start build bot-service. with USER: ${USER} ==============="

WORKDIR /app/

# Copying bot service
COPY --chown=${USER}:${USER} ../bot_microservice /app/

COPY ./scripts/start-bot.sh /app/
RUN chmod +x ./start-bot.sh

COPY --from=compile-image /app/.venv /app/.venv

USER ${USER}

ENV PATH="/app/.venv/bin:$PATH"


#===================== chat-service ================================
FROM compile-image as chat-service

RUN printf "================ Start build chat-service. with USER: ${USER} ==============="

WORKDIR /app/

USER ${USER}

# Copying bot service
COPY --chown=${USER}:${USER} ../chat_gpt_microservice /app/

COPY --from=compile-image /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN chmod -R 777 translations

CMD ["python3", "./run.py"]