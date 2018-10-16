FROM circleci/python

ADD requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

ADD app.py /app/