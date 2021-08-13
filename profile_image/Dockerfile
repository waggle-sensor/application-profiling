FROM waggle/plugin-base:1.1.1-ml-cuda10.2-l4t

RUN mkdir app


COPY tau.tgz /app/tau.tgz
COPY wrappertest.py /app/wrappertest.py
COPY profiler.sh /app/profiler.sh

WORKDIR /app

RUN tar -zxvf tau.tgz
WORKDIR /usr/lib/aarch64-linux-gnu
RUN mkdir pylib
RUN cp libpython3.6m.so pylib
WORKDIR /app/tau-2.30.1
RUN ./configure -pythoninc=/usr/include/python3.6m -pythonlib=/usr/lib/aarch64-linux-gnu/pylib -c++=g++ -cc=gcc
ENV PATH="/app/tau-2.30.1/arm64_linux/bin:$PATH"
RUN make install
ENV PYTHONPATH=/app/tau-2.30.1/arm64_linux/lib/bindings-python

COPY test.py /app/test.py
COPY stats.py /app/stats.py
COPY parser.py /app/parser.py

RUN pip install psutil

WORKDIR /app
RUN chmod +x profiler.sh

ENTRYPOINT ["/bin/sh"]
