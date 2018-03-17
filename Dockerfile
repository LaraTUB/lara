FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

ENV STATIC_PATH /app/app/static/

COPY ./app /app