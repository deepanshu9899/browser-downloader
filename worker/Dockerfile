FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir redis==5.1.1
COPY worker.py ./
CMD ["python", "worker.py"]
