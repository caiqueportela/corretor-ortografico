FROM python:3.8

WORKDIR /app

COPY requirements.txt .

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install -r requirements.txt

RUN python -m nltk.downloader all

COPY . /app

EXPOSE 5001

CMD [ "python", "app.py" ]