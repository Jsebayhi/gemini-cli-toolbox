FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    bats \
    curl \
    git \
    coreutils \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

ENTRYPOINT ["bats"]
