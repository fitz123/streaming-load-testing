from locustio/locust:latest

WORKDIR /opt/streamrapist

COPY requirements.txt /opt/streamrapist

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

COPY load_generator /opt/streamrapist/load_generator
