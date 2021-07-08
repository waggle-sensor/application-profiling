FROM waggle/plugin-base:1.1.1-ml-cuda10.2-l4t

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# apex supports multi precision training/inference for Tensor cores
# if we want to use fp16 models we need this as long as we use Nvidia's torch hub
# NOTE: pip3 install apex does not work as of Oct 2020 so install from git
# NOTE: installing apex requires nvcc which isn't in runtime Nvidia Docker
#       it needs devel version of Docker
# NOTE: Pytorch 1.6.0 does not support fp16 on CPU
#       https://github.com/open-mmlab/mmdetection/issues/2951#issuecomment-641024130
#RUN cd /tmp \
#  && git clone https://www.github.com/nvidia/apex \
#  && cd apex \
#  && python3 setup.py install \
#  && rm -rf /tmp/apex
#
#COPY apex-0.1-py3-none-any.whl /tmp/
#RUN cd /tmp \
# && pip3 install apex-0.1-py3-none-any.whl

COPY PyTorch /app/PyTorch
COPY hubconf.py app.py category_names.txt /app/

ARG SAGE_STORE_URL="HOST"
ARG SAGE_USER_TOKEN="-10"
ARG BUCKET_ID_MODEL="BUCKET_ID_MODEL"

ENV SAGE_STORE_URL=${SAGE_STORE_URL} \
    SAGE_USER_TOKEN=${SAGE_USER_TOKEN} \
    BUCKET_ID_MODEL=${BUCKET_ID_MODEL}

#RUN sage-cli.py storage files download ${BUCKET_ID_MODEL} coco_ssd_resnet50_300_fp32.pth --target /app/coco_ssd_resnet50_300_fp32.pth
#RUN sage-cli.py --target /app/coco_ssd_resnet50_300_fp32.pth
COPY coco_ssd_resnet50_300_fp32.pth /app/coco_ssd_resnet50_300_fp32.pth
COPY tau.tgz /app/tau.tgz
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
COPY wrappertest.py /app/wrappertest.py
COPY tauprofiler.sh /app/tauprofiler.sh

WORKDIR /app
RUN chmod +x tauprofiler.sh
ENTRYPOINT ["./tauprofiler.sh"]
#ENTRYPOINT ["python3","/app/app.py"]
#ENTRYPOINT ["python3", "wrappertest.py", "/app/app.py"]
