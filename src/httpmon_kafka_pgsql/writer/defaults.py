kafkaConsumerDefaults = {
  'bootstrap_servers': '127.0.0.1:9092',
  'security_protocol': 'SSL',
  'ssl_cafile': 'config/ca.pem',
  'ssl_certfile': 'config/monitoring-service.crt',
  'ssl_keyfile': 'config/monitoring-private.key',
  'topic': 'monitoring',
  'consumer_group': 'monitoring',
  'batch_timeout_ms': 10000
}

postgreSQLDefaults = {
  'dsn': 'postgres://user:password@127.0.0.1:22963/database?sslmode=require'
}