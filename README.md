# Credit Limit System

### Overview

This system processes users’ emotional and thought data broadcasted from devices to a Kafka topic and stores them in a PostgreSQL database. The system consists of:

	1.	A Flask web server for user-facing services and managing API requests.
	2.	A Kafka consumer process that listens for messages on a Kafka topic and inserts emotional and thought data into the database.

Prerequisites

	•	Python 3.9+
	•	Kafka (locally or remotely hosted)
	•	PostgreSQL (locally or remotely hosted)
	•	Docker

### Installation

##### Step 1: Clone the Repository and Create a virtualenv
```shell
git clone https://github.com/your-repo/credit-limit-system.git
cd credit-limit-system
python3 -m venv venv
source venv/bin/activate
```


##### Step 2: Install Python Dependencies

```shell
pip install -r requirements.txt
```

##### Step 3: Environment Variables Setup

Create a .env file in the root directory to configure environment variables as shown in `.env.sample`

##### Step 4: Kafka Setup

If Kafka is not installed, follow the [Kafka Quickstart](https://kafka.apache.org/quickstart) to install it locally or set it up in a Docker container.

Ensure the topic you want to consume from is created:

```
kafka-topics.sh --create --topic your_kafka_topic --bootstrap-server localhost:9092
```

### Running the System

You only need one command to start the system. Starting the web server also starts the kafka consumer on a separate process. 
The process is automatically terminated when the server is shutdown. Run the command below to start the system:

```shell
gunicorn --bind 0.0.0.0:8080 src.app:app
```
This will start the Flask web server on http://localhost:8080.

##### Using Docker
To build the Docker image for this application, navigate to the root directory where the `Dockerfile` is located and run the following command:

```shell
docker build -t credit-limit-system .
```

To run the container, use the following command:
```shell
docker run -p 8080:8080 --name credit-limit-system --env-file .env credit-limit-system
```

### Error Handling

##### Kafka Consumer Error Handling

Message Processing Failures: Each message is wrapped in a try-except block. In case of errors (e.g., malformed data, DB issues), log the error and continue processing the next message to avoid stopping the consumer.

##### API Error Handling

The appropriate http status code is returned for different types of errors (e.g. 500, 400, 401, 503).
All error response payloads are returned in the format: 
```json
{"message": "Service is unavailable"}
```

### Testing
To run the tests, execute the command below in the base directory:
```shell
pytest tests
```