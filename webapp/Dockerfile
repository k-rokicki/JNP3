FROM python:3.6

COPY ./jnp3_site .

RUN pip install -r ./requirements.txt

RUN mkdir /photos_to_upload

EXPOSE 1234

CMD ["python", "manage.py", "runserver", "0.0.0.0:1234"]