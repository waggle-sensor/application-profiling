FROM waggle/plugin-base:1.1.1-ml-cuda10.2-l4t
 
RUN apt update -y
RUN apt install -y gcc g++ zlib1g-dev autoconf automake make m4 libpython3.6-dev python3-dev wget
RUN wget http://tau.uoregon.edu/tau.tgz && tar -zxvf tau.tgz
WORKDIR /tau-2.31.1
RUN ./configure -bfd=download -python -pythonlib=/usr/lib/python3.6/config-3.6m-aarch64-linux-gnu -pythoninc=/usr/include/python3.6m -unwind=download -c++=g++ -cc=gcc
ENV PATH="/tau-2.31.1/arm64_linux/bin:$PATH"
RUN make -j4 install
ENV PYTHONPATH=/tau-2.31.1/arm64_linux/lib/bindings-python

COPY firstprime.py profiler.py runtime_metrics.py tau_parser.py /app/

RUN apt install default-jre
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
RUN apt-get update && apt-get install -y vim
RUN pip install -U jetson-stats && python -m pip install psutil && pip install schedule
RUN pip install -U pywaggle==0.54.0a1
 
WORKDIR /app
 
## Uncomment either of the two 

## Profile without TAU
CMD ["sh", "-c", "python profiler.py 'python firstprime.py'"]

## Profile with TAU 
#CMD ["sh", "-c", "python profiler.py 'tau_python -ebs -T serial,python firstprime.py’ local”]
