FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py ./
COPY app ./app
COPY phishhook ./phishhook
COPY data ./data
# Source uploads may retain a restrictive shell umask; appuser must be able
# to read Python modules and data and traverse their directories.
RUN useradd --create-home appuser \
    && chmod -R a+rX /app
USER appuser
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
