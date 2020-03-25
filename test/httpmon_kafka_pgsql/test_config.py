import pytest
from httpmon_kafka_pgsql.core.config import config

from httpmon_kafka_pgsql.agent.defaults import siteDefaults

import sys
import copy

@pytest.fixture()
def loadConfig():
  #Load sample configuration file
  config.load('../config/config.sample.yaml')

def test_getSetting(loadConfig):
  #Test default settings
  assert config.getSetting('doesNotExist', 'Test') == "Test"
  assert config.getSetting('loglevel', 'Test') == "ERROR"

def test_getDBConfig(loadConfig):
  #Test retrieval of DB config
  assert config.getDBConfig('writer')

def test_getKafka(loadConfig):
  #Ensure we get a valid Kafka config
  assert config.getKafkaConfig('monitoring')

def test_getTargets(loadConfig):
  #Ensure we receive url and associated config data
  assert len(config.getTargets()) > 0

def testDefaults(preDefaults, postDefaults):
  #Ensure defaults are populated with the specified entries
  count=0
  for url, configData in preDefaults:
    assert url is not None
    for key in postDefaults[count][1].keys():
      if key not in configData:
        assert key in postDefaults[count][1]
    count = count+1

def test_setDefaults(loadConfig):
  #Test setting defaults for Agent - web sites
  preDefaults = copy.deepcopy(list(config.getTargets()))
  config.setDefaults('websites', siteDefaults)
  postDefaults = list(config.getTargets())
  testDefaults(preDefaults, postDefaults)

# Make the script executable.
if __name__ == "__main__":
  raise SystemExit(pytest.main([__file__]))
