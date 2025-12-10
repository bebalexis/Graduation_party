FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# create qr folder at build time
RUN mkdir -p static/qr_codes
EXPOSE 5000
# Render sets $PORT; gunicorn will use it
#CMD ["gunicorn","--bind","0.0.0.0:$PORT","app:app","--workers","2"]
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT app:app --workers 2"]
