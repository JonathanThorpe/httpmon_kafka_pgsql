#Handles basic YAML configuration file including setting defaults
import yaml

class Config:
  settings = {}

  def setDefaults(self, setting, defaults):
    #Apply some reasonable defaults which do not have parameters set
    if setting in self.settings:
      for config in self.settings[setting].values():
        for defaultKey, defaultVal in defaults.items():
          if defaultKey not in config:
            config[defaultKey] = defaultVal
              
  def getTargets(self):
    #Returns: targets to monitor as k=URL, v=config parameters
    return(self.settings['websites'].items())

  def getKafkaConfig(self, name):
    #Returns: specified Kafka config
    return(self.settings['kafka'][name])

  def getDBConfig(self, name):
    #Returns: specified DB config
    return(self.settings['database'][name])

  def getSetting(self, setting, default):
    #Returns: either the specified value or the default
    if setting in self.settings:
      return self.settings[setting]
    else:
      return default

  def load(self, configFile):
    #Load the configuration file
    with open(configFile, 'r') as fh:
      self.settings = yaml.load(fh, Loader=yaml.SafeLoader)

config = Config()
