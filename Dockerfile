FROM jupyter/base-notebook

USER root

RUN pip install -r requirements

USER $NB_UID
