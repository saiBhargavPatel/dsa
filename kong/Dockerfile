FROM kong:3.9

# Declarative (DB-less) mode. The actual config is rendered at runtime
# from kong.yml by entrypoint.sh using the *_HOSTPORT env vars.
ENV KONG_DATABASE=off

# Copy the template and the runtime-rendering entrypoint.
COPY kong.yml /kong/declarative/kong.yml
COPY entrypoint.sh /kong/entrypoint.sh
RUN chmod +x /kong/entrypoint.sh

# Kong proxy listens on 8000 (Render routes public HTTPS here).
# Admin API is disabled for the public gateway (DB-less mode doesn't need it).
EXPOSE 8000

ENTRYPOINT ["/kong/entrypoint.sh"]
