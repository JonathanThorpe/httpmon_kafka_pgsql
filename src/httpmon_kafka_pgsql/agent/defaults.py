#This file contains defaults which are applied through the config core.config module's setDefaults function.

siteDefaults = {
  'valid_status_codes': [ 200 ],
  'regex': '',
  'timeout': 120,
  'frequency': 60
}

kafkaProducerDefaults = {
  'bootstrap_servers': '127.0.0.1:9092',
  'security_protocol': 'SSL',
  'ssl_cafile': 'config/ca.pem',
  'ssl_certfile': 'config/monitoring-service.crt',
  'ssl_keyfile': 'config/monitoring-private.key',
  'topic': 'monitoring',
  'consumer_group': 'monitoring',
  'acks': 1,
  'request_timeout_ms': 40000
}