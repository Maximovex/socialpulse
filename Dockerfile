FROM python:3.14-slim


WORKDIR /app
# Install uv

RUN pip install uv
# Copy dependency files first (layer caching)
COPY pyproject.toml .

# Install dependencies
RUN uv sync --no-dev

# Copy application code
COPY . .

# Expose API port
EXPOSE 8000

# Run FastAPI
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]