FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY ./app/requirements.txt /app/requirements.txt
RUN pip install --upgrade -r requirements.txt

COPY ./app /app