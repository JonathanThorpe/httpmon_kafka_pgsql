import asyncio
import asyncpg

class MonPostgresSQL:
  config = None
  connection = None

  async def connect(self):
    self.connection = await asyncpg.connect(self.config['dsn'])
  
  def __init__(self, config):
    self.config = config
