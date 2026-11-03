FROM golang:1.24 AS build
ARG MINIO_REF=7aac2a2c5b7c882e68c1ce017d8256be2feea27f
RUN git clone https://github.com/minio/minio.git /src && cd /src && git checkout "$MINIO_REF"
WORKDIR /src
ENV CGO_ENABLED=0
RUN go build -trimpath -o /minio .
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl && rm -rf /var/lib/apt/lists/*
COPY --from=build /minio /usr/local/bin/minio
RUN useradd -u 10001 -m minio && mkdir /data && chown minio /data
USER minio
EXPOSE 9000
ENTRYPOINT ["minio"]
CMD ["server", "/data", "--console-address", ":9001"]
