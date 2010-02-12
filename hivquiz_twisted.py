from alexandria.twisted.service import SSMIService
from hivquiz import ms
from twisted.internet import reactor
from twisted.python import log
from ssmi import SSMIFactory
import os, sys

log.startLogging(sys.stdout)

TRUTEQ_HOSTNAME = os.environ['TRUTEQ_HOSTNAME']
TRUTEQ_PORT = int(os.environ['TRUTEQ_PORT'])
TRUTEQ_USERNAME = os.environ['TRUTEQ_USERNAME']
TRUTEQ_PASSWORD = os.environ['TRUTEQ_PASSWORD']

print TRUTEQ_HOSTNAME, TRUTEQ_PORT, TRUTEQ_USERNAME, TRUTEQ_PASSWORD

def app_register(ssmi_protocol):
    SSMIService(ms, TRUTEQ_USERNAME, TRUTEQ_PASSWORD) \
                        .register_ssmi(ssmi_protocol)

reactor.connectTCP(
    TRUTEQ_HOSTNAME, 
    TRUTEQ_PORT, 
    SSMIFactory(app_register_callback=app_register)
)
reactor.run()
