FROM python

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt update && apt install -y chromium xvfb && pip install -r requirements.txt && rm requirements.txt

COPY ./app .

CMD [ "python", "-u", "-m", "main" ]
