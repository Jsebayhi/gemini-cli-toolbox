FROM debian:bookworm-slim

# Install dependencies for building kcov and running tests
RUN apt-get update && apt-get install -y --no-install-recommends \
    bats \
    curl \
    git \
    coreutils \
    ca-certificates \
    cmake \
    make \
    g++ \
    pkg-config \
    libdw-dev \
    binutils-dev \
    libcurl4-openssl-dev \
    zlib1g-dev \
    libiberty-dev \
    libssl-dev \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Build and install kcov from source (v42 is stable and supports modern Bash)
WORKDIR /tmp
RUN curl -sL https://github.com/SimonKagstrom/kcov/archive/refs/tags/v42.tar.gz | tar -xz && \
    cd kcov-42 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install && \
    cd /tmp && \
    rm -rf kcov-42

WORKDIR /code

# Pre-download bats-support and bats-assert for CI speed
RUN mkdir -p /code/tests/bash/libs && \
    curl -sL https://github.com/bats-core/bats-support/archive/refs/tags/v0.3.0.tar.gz | tar -xz -C /code/tests/bash/libs && \
    mv /code/tests/bash/libs/bats-support-0.3.0 /code/tests/bash/libs/bats-support && \
    curl -sL https://github.com/bats-core/bats-assert/archive/refs/tags/v2.1.0.tar.gz | tar -xz -C /code/tests/bash/libs && \
    mv /code/tests/bash/libs/bats-assert-2.1.0 /code/tests/bash/libs/bats-assert

# We keep bats as the entrypoint for backward compatibility if run manually,
# but the Makefile will now wrap it with kcov.
ENTRYPOINT ["bats"]
