FROM python:3.12.1 AS compile-image

ARG USER=web
ARG STAGE

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    DOCKER_CONTAINER=1 \
    POETRY_VERSION=1.7.1

RUN printf "================ Start build base service. with USER: ${USER}, STAGE: ${STAGE} ===============" \
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
    ffmpeg \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app/

RUN if [ "$USER" != "root" ]; then \
      mkdir /home/${USER} \
      && groupadd -r ${USER} && useradd -d /home/${USER} -r -g ${USER} ${USER} \
      && chown ${USER}:${USER} -R /home/${USER} /app; \
    fi

COPY --chown=${USER}:${USER} ../poetry.lock ../pyproject.toml /app/

RUN pip install --upgrade pip && pip install poetry==$POETRY_VERSION
RUN poetry config virtualenvs.in-project true && \
    poetry config virtualenvs.create true && \
    poetry install $(if [ "$STAGE" = "production" ]; then echo "--only main"; fi) --no-interaction --no-ansi --no-root && \
    rm -rf $POETRY_CACHE_DIR


#==================== bot-service =================================
FROM compile-image as bot-service

RUN printf "================ Start build bot-service. with USER: ${USER} ==============="

WORKDIR /app/

# Copying bot service
COPY --chown=${USER}:${USER} ../bot_microservice /app/
RUN mkdir "/app/shared" -p && chown ${USER}:${USER} -R /app/shared

COPY ./scripts/start-bot.sh /app/
RUN chmod +x ./start-bot.sh

COPY --from=compile-image /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

USER ${USER}
