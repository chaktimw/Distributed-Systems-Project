FROM python:3.6.8

ENV HOME /root
WORKDIR /root

COPY ../.. .

RUN pip3 install -r requirements.txt

EXPOSE 8201

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python subscriber.py