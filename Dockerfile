FROM circleci/python

USER root

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD app.py /runscope.py
