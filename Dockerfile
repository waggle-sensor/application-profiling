ARG APP_NAME
FROM chrispkraemer/tauprofiler:0.0.0 as builder

# ===== INSTALL TAU =====
#RUN mkdir tau
#COPY tau.tgz /tau/tau.tgz
#COPY wrappertest.py /tau/wrappertest.py
#WORKDIR /tau
#RUN tar -zxvf tau.tgz
#WORKDIR /usr/lib/aarch64-linux-gnu
#RUN mkdir pylib
#RUN cp libpython3.6m.so pylib
#WORKDIR /tau/tau-2.30.1
#RUN ./configure -pythoninc=/usr/include/python3.6m -pythonlib=/usr/lib/aarch64-linux-gnu/pylib -c++=g++ -cc=gcc
#ENV PATH="/tau/tau-2.30.1/arm64_linux/bin:$PATH"
#RUN make install
#ENV PYTHONPATH=/tau/tau-2.30.1/arm64_linux/lib/bindings-python
#WORKDIR /tau
#RUN chmod +x tauprofiler.sh
#ENTRYPOINT ["/bin/sh"]

ARG APP_NAME
#FROM waggle/plugin-objectcounter:0.0.0
FROM $APP_NAME

# ===== COPY OVER TAU INSTALL =====
COPY --from=builder /tau /tau
COPY --from=builder /usr/lib/aarch64-linux-gnu/pylib /usr/lib/aarch64-linux-gnu/pylib
ENV PATH="/tau/tau-2.30.1/arm64_linux/bin:$PATH"
ENV PYTHONPATH=/tau/tau-2.30.1/arm64_linux/lib/bindings-python

# ===== INSTALL TEGRASTATS BINARY =====
COPY tegrastats /usr/bin/tegrastats
WORKDIR /app
COPY tauprofiler.sh .

# ===== SETUP PROFILING SCRIPT =====
COPY --from=builder /tau/wrappertest.py /app/wrappertest.py
ENTRYPOINT ["./tauprofiler.sh"]

