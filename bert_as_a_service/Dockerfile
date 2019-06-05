FROM tensorflow/tensorflow:1.13.1-py3
RUN pip install bert-serving-server
COPY ./ /app
WORKDIR /app
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
CMD []
