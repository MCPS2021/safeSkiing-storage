FROM python:3.8
COPY ./*.py /code/
COPY ./config-docker.yml /code/config.yml
COPY ./requirements.txt /code/
WORKDIR code
RUN pip install -r requirements.txt
CMD ["python", "safeskiing_storage.py"]