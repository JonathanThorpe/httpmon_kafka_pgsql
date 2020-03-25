from subprocess import call
from sys import executable

import pytest
from httpmon_kafka_pgsql.core import cli

@pytest.fixture(params=("httpmon-kafka-pgsql",))
def command(request):
  #Return command to run
  return request.param

def test_parseArgs(command):
  # Call with the --help option as a basic sanity check.
  with pytest.raises(SystemExit) as exinfo:
      cli.parseArgs(("{:s}".format(command), "--help"))
  assert 0 == exinfo.value.code
  return

# Make the script executable.
if __name__ == "__main__":
  raise SystemExit(pytest.main([__file__]))
