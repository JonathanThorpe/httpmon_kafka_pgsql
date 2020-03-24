import argparse
import sys

#Set up the argument parser
parser = argparse.ArgumentParser(description='Run the application as either the agent (producer) or the receiver (consumer, DB writer)')

parser.add_argument('-c', '--config',
                    type=str,
                    default='config.yaml',
                    help='specify the configuration file')

parser.add_argument('-m', '--mode',
                    type=str,
                    choices=['agent', 'writer', 'init-schema', 'dbdump'],
                    help='''run as monitoring agent or writer.
                    agent: run as the monitoring agent,
                    writer: database writer / consumer,
                    init-schema: initialise the PostgreSQL database schema.
                    dbdump: dump database contents''')

args = parser.parse_args()
