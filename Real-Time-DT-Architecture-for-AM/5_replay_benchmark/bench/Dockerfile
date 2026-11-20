FROM python:3.11-slim
RUN pip install --no-cache-dir "paho-mqtt>=2.0" psycopg2-binary pandas numpy requests
COPY bench.py /bench.py
CMD ["python", "-u", "/bench.py"]
