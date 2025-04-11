FROM python:3.13
ENV PYTHONUNBUFFERED=1
RUN apt-get update \
&& apt-get clean

RUN pip install --upgrade pip
RUN mkdir app
WORKDIR app
copy . /app/
# RUN cd app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9000

