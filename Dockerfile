FROM python:alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt && rm requirements.txt

COPY ./app .

CMD [ "python", "-u", "main.py" ]
