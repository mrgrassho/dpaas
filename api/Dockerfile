FROM python:3.9

WORKDIR /code

COPY api/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY dpaas_core /code/dpaas_core
COPY api/app /code/app

ENV PYTHONPATH=/code

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
