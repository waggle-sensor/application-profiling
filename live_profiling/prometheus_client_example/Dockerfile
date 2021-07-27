FROM waggle/plugin-base:1.1.1-ml-cuda10.2-l4t

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r /app/requirements.txt

#COPY app.py /app/
#COPY tegrastats /usr/bin/tegrastats

COPY live_metrics_prometheus_client.py /app

ENTRYPOINT ["python3", "/app/live_metrics_prometheus_client.py"]
