import sys
from .defaults import kafkaProducerDefaults, siteDefaults
from ..core.config import config
from ..core.logger import logger
from .http_monitor import HTTPMonitor
from .mon_producer import MonProducer
import asyncio
import uuid

def initEventLoop():
  #Start a new asyncio event loop
  eventLoop = asyncio.get_event_loop()

  #Retrieve the Kafka configuration for the agent - defaults applied where
  #applicable at this point.
  monProducer = MonProducer(config.getKafkaConfig('monitoring'), eventLoop)
  
  #Iterate through each of the web sites that we want to monitor
  for url, configData in config.getTargets():
    logger.info('Setting up monitoring for %s' % (url))
    #Create a new object from the HTTPMonitor class
    currMonitor = HTTPMonitor(url, configData, eventLoop, monProducer.emit)

    #Start the HTTP monitor for the selected site.
    currMonitor.start()
  
  #Keep running the event loop until interrupted
  eventLoop.run_forever()

def main():
  #Load defaults for anything that hasn't been specified
  #in the configuration file
  config.setDefaults('websites', siteDefaults)
  config.setDefaults('kafka', kafkaProducerDefaults)

  #Start the event loop
  initEventLoop()