FROM circleci/python

USER root

ADD requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

ADD app.py /app/runscope.py
