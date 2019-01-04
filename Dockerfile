FROM python:3.6
LABEL maintainer="sridhar.rao@spirent.com"

ENV GRPC_PYTHON_VERSION 1.4.0
RUN python -m pip install --upgrade pip
RUN pip install grpcio==${GRPC_PYTHON_VERSION} grpcio-tools==${GRPC_PYTHON_VERSION}
RUN pip install paramiko
RUN pip install chainmap
RUN pip install oslo_utils
RUN pip install scp

WORKDIR /usr/src/app

COPY ./vsperf ./vsperf

EXPOSE 50051

CMD ["python", "./vsperf/vsperf-controller.py"]
