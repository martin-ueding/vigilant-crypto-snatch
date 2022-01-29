FROM python:3.10
RUN pip install vigilant-crypto-snatch
ENTRYPOINT ["vigilant-crypto-snatch"]
