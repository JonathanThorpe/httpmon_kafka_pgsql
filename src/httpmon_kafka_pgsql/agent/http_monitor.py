import asyncio
import aiohttp
import time
from datetime import datetime
from aiohttp.client_exceptions import ClientConnectorError
import re
from ..core.logger import logger

class HTTPMonitor:
  url = ''
  config = {}
  eventLoop = None
  regex = None

  async def testTarget(self):
    #Tests a HTTP(S) target

    result = {
      'ts': None,
      'regexResult': False,
      'responseTime': 0,
      'responseCode': 0,
      'errorMessage': None,
      'url': self.url
    }

    async with aiohttp.ClientSession() as session:
      while True:
        logger.debug('Connect to target target %s' % (self.url))
        try:
          result['ts'] = str(datetime.utcnow())
          timeStart = time.time() * 1000
          async with session.get(self.url, timeout=self.config['timeout']) as response:
            if (self.regex is not None):
              result['regexResult'] = self.regex.search(await response.text(), re.MULTILINE) is not None
            result['responseCode'] = response.status
            
        except ClientConnectorError as error:
          result['errorMessage'] = str(error)
        except asyncio.TimeoutError as error:
          result['errorMessage'] = ('Timeout occurred after %d seconds' % (self.config['timeout']))
        finally:
          #We're working in ms, so the additional work (e.g. regex matching) that takes place after a successful
          #get request is not considered to make a substantial difference to time calculations. We still want
          #to capture time taken even if we get an error as this may yield some interesting context.
          result['responseTime'] = (time.time() * 1000) - timeStart

          if (result['errorMessage']):
            logger.error('Error %s' % (result['errorMessage']))
          await self.callback(result)

        logger.debug('Task going to wait for %d seconds for %s' % (self.config['frequency'], self.url))
        await asyncio.sleep(self.config['frequency'])

  def start(self):
    self.eventLoop.create_task(self.testTarget())

  def __init__(self, url, config, eventLoop, callback):
    self.url = url
    self.config = config
    self.eventLoop = eventLoop
    self.callback = callback

    #If the site has a regex specified in the configuration, pre-compile it once.
    if self.config['regex']:
      self.regex = re.compile(self.config['regex'])
