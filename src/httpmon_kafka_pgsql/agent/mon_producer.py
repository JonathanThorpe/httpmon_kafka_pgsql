from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context
import json
import uuid

class MonProducer:
  eventLoop = None
  config = None
  producer = None
  sslContext = None
  agentUUID = None

  async def emit(self, result):
    data = {**result, **{
      'agentUUID': self.agentUUID
    }}

    await self.producer.send_and_wait(self.config['topic'],
                                      json.dumps(data).encode('UTF-8'))

  def getSSLContext(self):
    return(create_ssl_context(
      cafile = self.config['ssl_cafile'],
      certfile = self.config['ssl_certfile'],
      keyfile = self.config['ssl_keyfile']
    ))
  
  async def initProducer(self):
    self.producer = AIOKafkaProducer(
      loop = self.eventLoop,
      bootstrap_servers=self.config['bootstrap_servers'],
      security_protocol="SSL",
      ssl_context=self.sslContext,
      acks=self.config['acks']
    )

    await self.producer.start()

  def __init__(self, config, eventLoop, agentUUID=None):
    self.config = config
    self.eventLoop = eventLoop
    self.sslContext = self.getSSLContext()

    #Generate a unique runtime UUID for the agent 
    self.agentUUID = agentUUID or str(uuid.uuid4())

    self.initTask = self.eventLoop.create_task(self.initProducer())
    self.eventLoop.run_until_complete(self.initTask)
    