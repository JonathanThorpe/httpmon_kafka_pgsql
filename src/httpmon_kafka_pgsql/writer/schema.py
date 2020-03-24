from .defaults import postgreSQLDefaults
from ..core.config import config
from ..core.logger import logger
from .mon_consumer import MonConsumer
import asyncio
from .mon_pg import MonPostgresSQL
import json

schema = """
CREATE TABLE mon_daily (
  ts timestamp NOT NULL, 
  agent uuid NOT NULL,
  url VARCHAR(2048) NOT NULL,
  regexResult BOOLEAN NULL,
  responseCode INT,
  responseTime INT,
  errorMessage VARCHAR(256),
  PRIMARY KEY(ts, agent, url)
);

CREATE INDEX mon_daily_url ON mon_daily (url);
"""
async def createSchema():
  pg = MonPostgresSQL(config.getDBConfig('writer'))
  await pg.connect()
  await pg.connection.execute(schema)
  await pg.connection.close()

async def dumpDBasJSON():
  pg = MonPostgresSQL(config.getDBConfig('writer'))
  await pg.connect()
  results = await pg.connection.fetch('SELECT * FROM mon_daily')
  for result in results:
    print(dict(result))

  await pg.connection.close()

def init():
  #Load defaults for anything that hasn't been specified
  #in the configuration file
  config.setDefaults('database', postgreSQLDefaults)

  #Start the event loop
  return asyncio.get_event_loop()

def dbDump():
  eventLoop = init()
  eventLoop.run_until_complete(dumpDBasJSON())

def schemaInit():
  eventLoop = init()
  eventLoop.run_until_complete(createSchema())
