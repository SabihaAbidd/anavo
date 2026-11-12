# ANAVO backend: FastAPI + Qiskit Aer + exact classical solver.
# Used by Render (render.yaml) or any Docker host. The frontend deploys separately (Vercel).
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app
COPY requirements-lock.txt .
RUN pip install --upgrade pip && pip install -r requirements-lock.txt

COPY backend/ backend/
COPY src/ src/
COPY data/ data/

RUN useradd --create-home --uid 1000 anavo
USER anavo

EXPOSE 8000
# One worker: the job queue and optimization slot live in process memory.
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
