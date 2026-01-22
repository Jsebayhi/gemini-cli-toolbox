# Tier 2: The "Stack" Image
# Aggregates heavy SDKs (Java, Go) so they are cached efficiently.

# --- Stage 1: Harvest Artifacts ---
FROM eclipse-temurin:8-jdk-jammy AS java8
FROM eclipse-temurin:17-jdk-jammy AS java17
FROM eclipse-temurin:21-jdk-jammy AS java21
FROM golang:1.24-bookworm AS golang
FROM maven:3.9.6-eclipse-temurin-17 AS maven

# --- Stage 2: Build the Stack ---
FROM gemini-cli-toolbox/base:latest

# 1. Setup Directories
RUN mkdir -p /opt/sdks/java /opt/sdks/go /opt/sdks/maven

# 2. Copy Java Runtimes (Securely from official images)
COPY --from=java8  /opt/java/openjdk /opt/sdks/java/8
COPY --from=java17 /opt/java/openjdk /opt/sdks/java/17
COPY --from=java21 /opt/java/openjdk /opt/sdks/java/21

# 3. Copy Golang
COPY --from=golang /usr/local/go /opt/sdks/go

# 4. Copy Maven
COPY --from=maven /usr/share/maven /opt/sdks/maven

# 5. Install Dependencies (SDKMAN + Google Cloud SDK)
# - zip, unzip, curl, bash: For SDKMAN
# - apt-transport-https, gnupg: For GCloud repo security
RUN apt-get update && apt-get install -y \
    zip unzip curl bash \
    apt-transport-https ca-certificates gnupg

# 5.1 Install Google Cloud SDK (Modern 'signed-by' method)
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get update && apt-get install -y google-cloud-cli && \
    rm -rf /var/lib/apt/lists/*

# 6. Install SDKMAN (Strictly for SBT/Scala)
ENV SDKMAN_DIR="/usr/local/sdkman"
RUN curl -s "https://get.sdkman.io" | bash
RUN echo "sdkman_auto_answer=true" > $SDKMAN_DIR/etc/config && \
    echo "sdkman_auto_selfupdate=false" >> $SDKMAN_DIR/etc/config

# 7. Install SBT and Scala via SDKMAN
# We use bash login shell to ensure SDKMAN environment is loaded
RUN bash -c "source $SDKMAN_DIR/bin/sdkman-init.sh && \
    sdk install sbt && \
    sdk install scala"

# 8. Setup Environment Variables & Path
# Default to Java 21 and Go
ENV JAVA_HOME=/opt/sdks/java/21
ENV GOROOT=/opt/sdks/go
ENV MAVEN_HOME=/opt/sdks/maven
ENV PATH=$PATH:$GOROOT/bin:$JAVA_HOME/bin:$MAVEN_HOME/bin

# 8. Add 'use-java' helper for the Agent
# This allows 'source use-java 8' to work in the shell
RUN echo 'function use-java() { export JAVA_HOME=/opt/sdks/java/$1; export PATH=$JAVA_HOME/bin:$PATH; java -version; }' >> /etc/bash.bashrc
# Make SDKMAN available globally
RUN echo 'source /usr/local/sdkman/bin/sdkman-init.sh' >> /etc/bash.bashrc

# 9. Fix Permissions
# Allow the 'gemini' user to write to SDKMAN (for installing more deps if asked)
RUN chmod -R 777 $SDKMAN_DIR
