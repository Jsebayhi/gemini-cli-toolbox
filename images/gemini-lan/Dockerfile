FROM alpine:latest

# Install socat for proxying
RUN apk add --no-cache socat

# Add standardized logging and watchdog logic
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Entrypoint handles watchdog and starts socat
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
