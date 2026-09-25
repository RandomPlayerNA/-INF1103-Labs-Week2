FROM python:3.11-slim

RUN apt-get update \
	&& apt-get install -y --no-install-recommends git openssh-client ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY persistent_auditor.py .

CMD ["python", "persistent_auditor.py"]