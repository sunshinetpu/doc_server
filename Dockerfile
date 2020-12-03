FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /usr/src/app

# specifying the working dir inside the container
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy current dir's content to container's WORKDIR root i.e. all the contents of the web app
# ADD . /usr/src/app
COPY . .

ENTRYPOINT [ "python" ]

CMD [ "src/demo_service.py" ]