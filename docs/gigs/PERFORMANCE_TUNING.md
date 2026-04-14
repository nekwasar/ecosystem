# Performance Tuning

## Caching

- Enable caching to avoid redundant searches: `ENABLE_CACHE=true`
- Tune `CACHE_EXPIRY` based on freshness requirements (default: 3600s)
- Cache is in-memory — restarts clear it. Consider Redis for persistence.

## Concurrency

- Sources run concurrently via `Promise.allSettled` — all sources are queried in parallel
- Reduce `DEFAULT_RESULTS_WANTED` to lower per-source load
- Limit `DEFAULT_SITE_NAMES` to only the boards you need

## Logging

- Use `LOG_LEVEL=warn` or `LOG_LEVEL=error` in production to reduce I/O
- Use `LOG_LEVEL=debug` only for troubleshooting

## Rate Limiting

- Set `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_TIMEFRAME` based on traffic patterns
- Rate limiting adds minimal overhead (in-memory tracking)

## Node.js Tuning

- Increase `--max-old-space-size` for large result sets:
  ```bash
  NODE_OPTIONS="--max-old-space-size=4096" node dist/apps/api/main.js
  ```
- Use Node.js cluster mode or deploy multiple replicas behind a load balancer

## Docker

- Use multi-stage builds (already configured) to minimize image size
- Set appropriate resource limits in `docker-compose.yml`:
  ```yaml
  deploy:
    resources:
      limits:
        memory: 1G
        cpus: "1.0"
  ```

## Monitoring

- Poll `/health` to track uptime and memory usage
- Use `X-Process-Time` response header to identify slow requests
- Use `X-Request-Id` to trace requests across logs
