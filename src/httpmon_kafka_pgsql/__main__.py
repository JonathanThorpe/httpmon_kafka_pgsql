from .core.config import config
from .core.cli import parseArgs
from .core.logger import logger
from .agent.agent import main as agent
from .writer.writer import main as writer
from .writer.schema import dbDump, schemaInit

import os
import sys

def main():
  #Main entry point
  args = parseArgs(sys.argv[1:])
  config.load(args.config)
  logger.start(config.getSetting('loglevel', 'ERROR'))
  
  if args.mode == 'agent':
    return agent()
  elif args.mode == 'writer':
    return writer()
  elif args.mode == 'init-schema':
    return schemaInit()
  elif args.mode == "dbdump":
    return dbDump()

if __name__ == "__main__":
  raise SystemExit(main())
