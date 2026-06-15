FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
      edge-tts \
      mutagen \
      pydub

COPY scripts/epub2tts.py /usr/local/lib/epub2tts.py

# Adapted on 2026-06-13 from https://github.com/aedocw/epub2tts.
RUN printf '#!/bin/sh\nexec python /usr/local/lib/epub2tts.py "$@"\n' \
      > /usr/local/bin/epub2tts \
    && chmod +x /usr/local/bin/epub2tts

ENTRYPOINT ["epub2tts"]
CMD ["--help"]
