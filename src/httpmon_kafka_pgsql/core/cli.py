import argparse
import sys
from ..__version__ import __version__

#Set up the argument parser
parser = argparse.ArgumentParser(description='Run the application as either the agent (producer) or the receiver (consumer, DB writer)',
                                 prog=__name__)

parser.add_argument('-c', '--config',
                    type=str,
                    default='config/config.yaml',
                    help='specify the configuration file')

parser.add_argument('-v', '--version',
                    action='store_true',
                    help='show application version')

parser.add_argument('-m', '--mode',
                    type=str,
                    choices=['agent', 'writer', 'init-schema', 'dbdump'],
                    help='''run as monitoring agent or writer.
                    agent: run as the monitoring agent,
                    writer: database writer / consumer,
                    init-schema: initialise the PostgreSQL database schema.
                    dbdump: dump database contents''')

args = parser.parse_args()

if args.version:
  print('%s version %s' % (__name__, __version__))
  sys.exit(0)
elif args.mode is None:
  print('Error: %s mode must be specified.' % (__name__,))
  parser.print_help()
  sys.exit(1)
