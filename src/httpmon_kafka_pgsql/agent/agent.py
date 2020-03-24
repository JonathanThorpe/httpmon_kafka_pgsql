import sys
from .defaults import kafkaProducerDefaults, siteDefaults
from ..core.config import config
from ..core.logger import logger
from .http_monitor import HTTPMonitor
from .mon_producer import MonProducer
import asyncio
import uuid

def initEventLoop():
  eventLoop = asyncio.get_event_loop()
  monProducer = MonProducer(config.getKafkaConfig('monitoring'), eventLoop)
  
  for url, configData in config.getTargets():
    logger.info('Setting up monitoring for %s' % (url))
    currMonitor = HTTPMonitor(url, configData, eventLoop, monProducer.emit)
    currMonitor.start()
  
  eventLoop.run_forever()

def main():
  #Load defaults for anything that hasn't been specified
  #in the configuration file
  config.setDefaults('websites', siteDefaults)
  config.setDefaults('kafka', kafkaProducerDefaults)

  #Start the event loop
  initEventLoop()