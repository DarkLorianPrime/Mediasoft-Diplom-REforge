FROM python:3.11-buster
COPY app /application
WORKDIR /application

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install -C deployment --no-root --without=dev

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
