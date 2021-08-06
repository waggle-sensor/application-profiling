FROM waggle/plugin-base:1.1.1-ml-cuda10.2-l4t

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY app.py live_metrics.py /app/
COPY tegrastats /usr/bin/tegrastats

ENTRYPOINT ["python3", "/app/app.py"]
