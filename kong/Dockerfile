FROM kong:3.9

# DB-less Kong
ENV KONG_DATABASE=off

# Copy declarative configuration
COPY kong.yml /kong/declarative/kong.yml

# Copy entrypoint with executable permissions
COPY --chmod=755 entrypoint.sh /kong/entrypoint.sh

# Kong proxy
EXPOSE 8000

ENTRYPOINT ["/kong/entrypoint.sh"]