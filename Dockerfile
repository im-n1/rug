FROM jupyter/base-notebook

USER root

RUN pip install httpx

USER $NB_UID
