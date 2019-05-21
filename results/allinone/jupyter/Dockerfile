FROM jupyter/scipy-notebook

RUN python --version

RUN conda install --quiet --yes -c \
    conda-forge osmnx dask

RUN pip install -U json \
                   numpy \
                   collections \
                   glob \
                   graphviz \
                   paramiko \
                   tarfile \
                   stat \
                   math \
                   datetime \
                   urllib \
                   requests

VOLUME /notebooks
WORKDIR /notebooks
