FROM kong:3.9
ENV KONG_DATABASE=off
ENV KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml

COPY kong.yml /kong/declarative/kong.yml

EXPOSE 8000 8443 8001 8444