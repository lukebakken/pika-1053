FROM python:2.7.15-alpine3.7

# Copy and install dependencies
COPY requirements.txt ./
RUN pip install -r ./requirements.txt

# Set workdir. Script should be mounted.
WORKDIR /app

# Move app files inside image
COPY ./main.py ./producer.py ./

# Run container
ENTRYPOINT [ "python", "-u", "main.py" ]

# rabbitmq host based on environment (docker tip: use custom network)
# interval in seconds
CMD [ "-rmq=localhost", "-interval=300" ]
