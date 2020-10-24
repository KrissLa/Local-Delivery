FROM python:3.8.5

RUN mkdir /src
WORKDIR /src
COPY requirements.txt /src

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /src
