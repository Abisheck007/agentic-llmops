FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY frontend/requirements.txt /app/requirements.txt

RUN python -m pip install --no-cache-dir \
    -r /app/requirements.txt

COPY frontend/app.py /app/app.py

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]