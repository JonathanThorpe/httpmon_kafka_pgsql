from .defaults import kafkaConsumerDefaults, postgreSQLDefaults
from ..core.config import config
from ..core.logger import logger
from .mon_consumer import MonConsumer
from .mon_pg import MonPostgresSQL
import asyncio

def initEventLoop():
  #Create new event loop
  eventLoop = asyncio.get_event_loop()
  
  #Create a new PostgreSQL database connection based on the configuration
  pgsql = MonPostgresSQL(config.getDBConfig('writer'))

  #Start the monitoring consumer.
  monConsumer = MonConsumer(config.getKafkaConfig('monitoring'), eventLoop, pgsql)  
  
  #Start the consumer task
  monConsumer.start()

  #Run the event loop until interrupted
  eventLoop.run_forever()

def main():
  #Load defaults for anything that hasn't been specified
  #in the configuration file
  config.setDefaults('kafka', kafkaConsumerDefaults)
  config.setDefaults('database', postgreSQLDefaults)
  #Start the event loop
  initEventLoop()