FROM python:3.7.2-alpine3.8

WORKDIR /usr/src/app

COPY requirements.txt ./

# install sys dependency for pillow and shaape
RUN apk add build-base python3-dev jpeg-dev zlib-dev fontconfig ttf-dejavu py-cairo pango cairo py-gtk
ENV LIBRARY_PATH=/lib:/usr/lib

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi"]
