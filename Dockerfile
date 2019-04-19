FROM python:3.6.7

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python3", "./src/main.py" ]