FROM tailscale/tailscale:stable

# Add standardized logging and watchdog logic
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# We override the tailscale entrypoint with our own
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
