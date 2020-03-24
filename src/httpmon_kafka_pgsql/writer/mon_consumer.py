from ..core.logger import logger
from aiokafka import AIOKafkaConsumer
from aiokafka.helpers import create_ssl_context
import json
from datetime import datetime
import sys

class MonConsumer:
  eventLoop = None
  config = None
  consumer = None
  sslContext = None

  def getSSLContext(self):
    return(create_ssl_context(
      cafile = self.config['ssl_cafile'],
      certfile = self.config['ssl_certfile'],
      keyfile = self.config['ssl_keyfile']
    ))

  async def insertDB(self, value):
    ts = datetime.strptime(value['ts'], '%Y-%m-%d %H:%M:%S.%f')
    await self.pgsql.connection.execute('''INSERT INTO mon_daily
                                    (ts, agent, url, regexResult, responseCode, responseTime, errorMessage)
                                    VALUES ($1, $2, $3, $4, $5, $6, $7)''',
                                    ts,
                                    value['agentUUID'],
                                    value['url'],
                                    value['regexResult'],
                                    value['responseCode'],
                                    value['responseTime'],
                                    value['errorMessage'])

  async def batchDBWrite(self, messages):
    async with self.pgsql.connection.transaction():
      for msg in messages:
        #logger.debug('Message: %s %s %s %s %s %s' % (msg.topic, msg.partition, msg.offset,
        #                msg.key, msg.value, msg.timestamp))
        value = None
        try:
          value = json.loads(msg.value)
        except json.decoder.JSONDecodeError as error:
          logger.error('Unable to decode JSON: %s, error: %s' % (msg.value, str(error)))
        finally:
          if value:
            await self.insertDB(value)
  
  async def consumeMessages(self):
    # Consume messages
    while True:
      result = await self.consumer.getmany(timeout_ms = self.config['batch_timeout_ms'])
      for tp, messages in result.items():
        logger.debug("%d messages for processing on partition %d" % (len(messages), tp.partition))
        if messages:
          txOk = True
          try:
            #Could consider breaking up database transations into smaller chunks
            await self.batchDBWrite(messages)
          except KeyError as error:
            logger.critical('Malformed message - not committing topic: %s' % (str(error),))
            txOk = False
          except:
            error = sys.exc_info()[0]
            logger.critical('Unable to complete database transation - not committing topic: %s' % (str(error),))
            txOk = False
          
          if txOk:
            offset = messages[-1].offset + 1
            logger.debug("Committing topic partition %d with offset %d" % (tp.partition, offset))
            await self.consumer.commit({tp: offset})    

  async def initConsumer(self):
    await self.pgsql.connect()

    self.consumer = AIOKafkaConsumer(
      self.config['topic'],
      loop = self.eventLoop,
      bootstrap_servers = self.config['bootstrap_servers'],
      security_protocol = 'SSL',
      ssl_context = self.sslContext,
      group_id = self.config['consumer_group'],
      enable_auto_commit = False,
      auto_offset_reset='earliest'
    )

    try:
      await self.consumer.start()
      logger.info('Consumer started running with a batch timeout of %dms' % (self.config['batch_timeout_ms'],))
      self.consumeMessages()
    except:
      error = sys.exc_info()[0]
      logger.critical('Unable to consume messages - fatal error: %s' % (str(error),))
    finally:
      # Will leave consumer group;
      await self.consumer.stop()

  def __init__(self, config, eventLoop, pgsql):
    self.config = config
    self.eventLoop = eventLoop
    self.sslContext = self.getSSLContext()
    self.pgsql = pgsql

    self.initTask = self.eventLoop.create_task(self.initConsumer())
    self.eventLoop.run_until_complete(self.initTask)
    