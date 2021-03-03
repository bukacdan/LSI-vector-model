FROM python:3.7

COPY . /web

WORKDIR /web

RUN apt-get update -y

RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt

ENV FLASK_APP=.

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000" ]
