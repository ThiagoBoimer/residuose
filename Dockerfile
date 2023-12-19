FROM python:3.10-alpine3.16

ENV PYTHONUNBUFFERED 1
ENV PATH="/scripts:${PATH}"

COPY requirements.txt /requirements.txt
RUN apk add --upgrade --no-cache build-base linux-headers && \
    pip install --upgrade pip && \
    pip install -r /requirements.txt

COPY app/ /app
WORKDIR /app

COPY ./scripts /scripts
RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

# RUN adduser -u 1500 --disabled-password --no-create-home user
# RUN chown -R user:user /vol
# RUN chown -R user:user /app
# RUN chmod -R 777 /vol/web
# USER user

CMD ["entrypoint.sh"]