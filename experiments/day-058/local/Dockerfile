FROM python:3.12-slim
RUN pip install --no-cache-dir opensre==2026.4.5 && useradd -m -u 1000 runner
USER runner
ENV DO_NOT_TRACK=1 OPENSRE_ANALYTICS_DISABLED=1
WORKDIR /work
