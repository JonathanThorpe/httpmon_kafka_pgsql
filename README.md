
# HTTP Monitoring using Kafka and PostgreSQL
This is a small demonstration program developed to provide:

1. A simple **monitoring agent / Kafka producer** that:  
  a. Monitors HTTP(S) URLs, capturing response code, response time and optionally, whether or not the body of the response matches a specific regular expression.  
  b. Can monitor multiple URLs at the same time.  
  c. Produces messages to a Kafka topic for later consumption.  

2. A **Kafka consumer / PostgreSQL writer** which:  
  a. Consumes messages from a Kafka topic in a batch.  
  b. Using transactional logic, *attempts* to commit messages to the database before setting the offset on the topic.

## Requirements
This application requires Python 3 - dependent modules are specified in `requirements.txt` which may be installed with:
```
pip3 install -r requirements.txt
```
Other dependencies:
* Kafka Cluster which supports TLS
* PostgreSQL Database Server

## Configuration File
A sample configuration file is available in `config/config.sample.yaml`. Configuration directives are as follows.

### General Configuration
The following are configured at the top level of the configuration YAML file.
| Parameter     | Description |
| --------------| ------------- |
| loglevel | Log level can be one of: DEBUG, INFO, WARN, ERROR, CRITICAL (defaults to ERROR) |

### Kafka (Agent/Producer and Consumer/Writer)
Parameters are specified against `kafka: { monitoring: {<params>}` are as follows:
| Parameter     | Description |
| --------------| ------------- |
| bootstrap_servers | Kafka bootstrap servers specified as < host >:< port > |
| ssl_cafile | CA file for validating the connection to the Kafka cluster |
| ssl_certfile | Certificate file for authentication |
| ssl_keyfile | Private Key file for the above |
| topic | Kafka topic to produce messages to (Agent) or consume from (Writer) |

For the Agent/Producer, the following parameters are available:
| Parameter     | Description |
| --------------| ------------- |
| acks | Can be 0, 1, all or a number of replicas to replicate to. Default of 1 only waits for Leader to write the request. [more](https://github.com/aio-libs/aiokafka/blob/master/docs/producer.rst#retries-and-message-acknowledgement). |
| request_timeout_ms | Request timeout in ms - configure carefully to account for latency during rebalancing. Default: 40000 |


Also, for the Consumer/Writer, the following parameters are available:
| Parameter     | Description |
| --------------| ------------- |
| batch_timeout_ms | Milliseconds to timeout when batching transactions to the database. |

### Web Sites (Agent/Producer)
Web sites are specified as dictionaries of dictionaries within `websites` :
| Parameter     | Description |
| --------------| ------------- |
| valid_status_codes | Status codes that are considered valid. Default: 200 |
| regex | Regular expression to apply to the body of the response. Default: (none) |
| timeout | Timeout for connecting to the site (seconds). Default: 120 |
| frequency | How frequent to monitor the site (seconds). Default: 60 |

If specifying a site with defaults, ensure that the item is specified as an empty dictionary (e.g. "site": {})

### Database (Consumer/Writer)
| Parameter     | Description |
| --------------| ------------- |
| dsn | Connection string for connecting to PostgreSQL - e.g. `postgres://<user>:<password>@<host>:<port>/defaultdb?sslmode=require` |

## Running the Application
To keep the application simple and maximise code re-use, it has been packaged as several modules which can all by run form the same package.

### Command Line
Running the application from the console at the source tree is as follows:
```
usage: src.httpmon_kafka_pgsql.core.cli [-h] [-c CONFIG] [-v]
                                        [-m {agent,writer,init-schema,dbdump}]

Run the application as either the agent (producer) or the receiver (consumer,
DB writer)

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        specify the configuration file (Environment Variable:
                        APP_CONFIG).
  -v, --version         show application version
  -m {agent,writer,init-schema,dbdump}, --mode {agent,writer,init-schema,dbdump}
                        run as monitoring agent or writer (Environment
                        Variable: APP_MODE) agent: run as the monitoring
                        agent, writer: database writer / consumer, init-
                        schema: initialise the PostgreSQL database schema.
                        dbdump: dump database contents
```
The `--config` parameter can also be specified as the `APP_CONFIG` environment variable and refers to a path to the configuration YAML file.

The `--mode` parameter (also specifyable as `APP_MODE`) specifies how the program is run:
* **agent**: Runs as the HTTP Monitoring Agent / Producer.
* **writer**: Runs as the Consumer / Writer.
* **init-schema**: Creates the database schema. Does not drop the table if it already exists.
* **dbdump**: Dump the database contents.

### Docker Container
A `Dockerfile` is included which will build the image which can be run as follows:
```
docker build -t httpmon_kafka_pgsql:0.1.0 .
```
The default configuration expects a file in `config/config.yaml` so this file will either need to be added (i.e. modified from `config/config.sample.yaml`) or a volume configured for your Docker environment to map this to a file that exists.

#### Initialising the Database
To initialise the database, run the following:
```
docker run --rm -e "APP_MODE=init-schema" -it httpmon_kafka_pgsql:0.1.0
```

#### Dumping the Database
To dump the database contents, run the following:
```
docker run --rm -e "APP_MODE=dbdump" -it httpmon_kafka_pgsql:0.1.0
```

#### Docker-compose
A `docker-compose.yml` file is also included which will build the image and start up both the agent and writer. 

**Note that running `docker-compose up` assumes that the database has already been initialised. If you need to do this, run the container with the `APP_MODE=init-schema` first.**

## Design
### Monitoring Agent / Producer
Design considerations of the Monitoring Agent/Producer are as follows:
* Makes use of asynchronous I/O (asyncio, aoihttp, aiokafka) to perform asynchronous monitoring of multiple HTTP(S) URLs simultaneously without the overheads of running a traditional threading model.
* Monitors each URLs with different specified frequencies.
* Captures HTTP response time, HTTP response code, as well as whether or not the body includes a specified regex.

###  Consumer / Writer
* The writer does not commit to the topic until there has been a successful database transaction. This is intended to support reliable persistent storage of records. To do this, messages from the Kafka topic are handled in batches with a user-configurable batch timeout (milliseconds).
* A user configurable consumer group is configured to *help* ensure consume-once of messages on the topic.
* It is possible that in between handling the database transaction and setting the offset to the topic for the consumer group, another Consumer receives the same messages and also attempts to process the messages. The only mitigation here is that a database constraint based on *timestamp*, *agent uuid* (generated on startup) and *url* raises a handled uniqueness violation. 

### Areas of Improvement
#### HTTP Response Time Calculation
The monitoring agent naively determines the response time from the moment the GET request is issued to the endpoint to the moment a response has been received and checked for the presence for the optional regex. The following could be considered:
* Measuring response time for HTTP can include many things, including DNS resolution, time to first byte from the server, time to receive the body etc.
* The application runs a single aiohttp client session which takes advantage of connection pooling. This has the advantage of being more efficient, but does not account for delays resulting from slow DNS resolution for example.

#### Database Handling
The following can be improved with database handling:
* The Consumer/Writer simply dumps the data to a single table called `mon_daily`. There is no expiry of records, summarisation etc - you can do with the data as you wish for now.
* There is no control over how many inserts may be made per transaction. This could become quite large which, depending on the `batch_timeout_ms` setting, could result in multiple Consumers within a consumer group attempting to commit the same messages to the database. The constraints imposed by the composite primary key avoid duplicate records, but it's not very efficient. One way to balance this could be to specify a maximum number of messages per transaction and then regularly set the topic offset.

## Still to Come...
* Package properly
* Write tests

## Versioning
This project uses [SemVer](http://semver.org/) for versioning.

## Licence
This project is licenced under the MIT License - see the [LICENCE.md](LICENCE.md) file for details

## Acknowledgments
* [Application Template](https://github.com/mdklatt/cookiecutter-python-app) used with [cookiecutter](https://github.com/cookiecutter/cookiecutter). Mainly the Logger class in `src/core/logger.py` was used verbatim from this.

