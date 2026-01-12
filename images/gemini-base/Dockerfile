# Base Image for Gemini Toolbox
# Contains: Python (Latest Stable), Node.js 20, OS Security Updates, Gosu, Git

# --- Stage 1: Source Node.js ---
# We harvest the Node.js binaries from the official image to ensure they are correct
FROM node:20-bookworm-slim AS node-source

# --- Stage 2: Final Image ---
# We use 'python:slim' which always points to the LATEST stable Python version on Debian
# This satisfies the requirement: "not have to update the dockerfile... when there will be a new release"
FROM python:slim

ENV DEBIAN_FRONTEND=noninteractive

# 1. Install Node.js (Grafted from Stage 1)
# We copy /usr/local which contains bin/node, lib/node_modules, and bin/npm symlinks
COPY --from=node-source /usr/local /usr/local

# 2. System Updates & Essentials
# - make: Added per request
# - gosu: for user switching
# - git, procps, findutils: Standard agent toolkit
# - xsel: for /copy command
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    make \
    gosu \
    git \
    ca-certificates \
    procps \
    findutils \
    xsel \
    && rm -rf /var/lib/apt/lists/*

# 3. Configure Python for "Toolbox" Usage
# - Allow 'gemini' user (and others) to install packages globally
# - Disable the "externally managed environment" warning for pip
ENV PIP_BREAK_SYSTEM_PACKAGES=1
ENV PIP_ROOT_USER_ACTION=ignore

# Grant global write access to Python's install directories
# This allows 'pip install' to work immediately without sudo or --user
RUN chmod -R 777 /usr/local/lib/python* \
    && chmod 777 /usr/local/bin
