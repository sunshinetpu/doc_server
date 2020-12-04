FROM python:3.6

RUN mkdir -p /home/user/doc_app

COPY requirements.txt  /home/user/doc_app/requirements.txt

WORKDIR /home/user/doc_app

RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT [ "python3" ]
CMD [ "demo_service.py" ]