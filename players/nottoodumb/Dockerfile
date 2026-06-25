# Build Docker.
FROM alpine AS build

RUN apk add --no-cache build-base curl gcompat git nim

RUN if [ "$(apk --print-arch)" = "x86_64" ]; then \
    curl -fsSL \
      -o /usr/local/bin/nimby \
https://github.com/treeform/nimby/releases/download/0.1.26/nimby-Linux-X64; \
  elif [ "$(apk --print-arch)" = "aarch64" ]; then \
    curl -fsSL \
      -o /usr/local/bin/nimby \
https://github.com/treeform/nimby/releases/download/0.1.26/nimby-Linux-ARM64; \
  else \
    echo "unsupported arch: $(apk --print-arch)" && exit 1; \
  fi && \
  chmod +x /usr/local/bin/nimby && \
  nimby use 2.2.4

WORKDIR /workspace/among_them
COPY nimby.lock .
RUN nimby --global sync nimby.lock

COPY . .
RUN nim c \
  -d:release \
  -d:botHeadless \
  --nimcache:/tmp/bitworld-nimcache \
  --out:/tmp/nottoodumb \
  players/nottoodumb/nottoodumb.nim

# Run Docker.
FROM alpine

WORKDIR /workspace/among_them
COPY --from=build \
  /tmp/nottoodumb \
  /bin/nottoodumb
COPY --from=build /workspace/among_them/data ./data

CMD ["/bin/nottoodumb"]
