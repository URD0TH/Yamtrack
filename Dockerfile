FROM ghcr.io/astral-sh/uv:python3.12-alpine3.23

ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT="/usr/local"
ENV UV_SYSTEM_PYTHON=1

ARG VERSION=dev
ENV VERSION=$VERSION

WORKDIR /yamtrack

COPY ./pyproject.toml ./pyproject.toml
COPY ./uv.lock ./uv.lock

RUN uv sync --locked --no-dev

COPY ./entrypoint.sh /entrypoint.sh
COPY ./supervisord.conf /etc/supervisord.conf
COPY ./nginx.conf /etc/nginx/nginx.conf
# Generate a copy of the nginx config with IPv6 support.
RUN sed 's/listen 8000;/listen 8000; listen [::]:8000;/' /etc/nginx/nginx.conf > /etc/nginx/nginx.ipv6.conf

RUN apk add --no-cache nginx shadow \
    && chmod +x /entrypoint.sh \
    # create user abc for later PUID/PGID mapping
    && useradd -U -M -s /bin/sh abc \
    # Create required nginx directories and set permissions
    && mkdir -p /var/log/nginx \
    && mkdir -p /var/lib/nginx/body

# Upgrade pip to resolve base-image CVEs (app uses uv, not pip)
RUN uv pip install --upgrade pip

# Django app
COPY src ./
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["/entrypoint.sh"]

HEALTHCHECK --interval=45s --timeout=15s --start-period=30s --retries=5 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:8000/health/ || exit 1
