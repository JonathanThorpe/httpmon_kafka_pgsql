from aiokafka.helpers import create_ssl_context
from .logger import logger
import sys
from ssl import SSLError

def createSSLConext(cafile, certfile, keyfile):
  #Try to gracefully handle issues with creating SSL 
  sslContext = None
  try:
    sslContext = create_ssl_context(
      cafile = cafile,
      certfile = certfile,
      keyfile = keyfile
    )
  except FileNotFoundError as error:
    logger.critical('File not found while creating SSL context for Kafka - ensure your CA, Certificate file and Private Key are configured: %s' % (error,))
  except SSLError as error:
  #  error = sys.exc_info()[0]
    logger.critical('Unable to create SSL contact for Kafka - ensure your CA, Certificate file and Private key are valid: %s' % (error,))
  finally:
    if sslContext is not None:
      return(sslContext)
    else:
      sys.exit(1)