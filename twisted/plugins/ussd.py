from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application import internet
from twisted.application.service import IServiceMaker

from alexandria.twisted.ussd import SSMIService
from ssmi import SSMIFactory

class Options(usage.Options):
    optParameters = [
        ["username", "u", '', "SSMI username"],
        ["password", "pw", '', "SSMI password"],
        ["host", "h", '', "SSMI host"],
        ["port", "p", '', "SSMI host's port"],
    ]


class SSMIServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "ussd"
    description = "Run Alexandria over USSD"
    options = Options
    
    def makeService(self, options):
        # all are mandatory, if they haven't been provided, prompt for them
        for key in options:
            if not options[key]:
                options[key] = raw_input('%s: ' % key)
        
        def app_register(ssmi_protocol):
            return SSMIService(options['username'], options['password']) \
                                .register_ssmi(ssmi_protocol)
        
        return internet.TCPClient(options['host'], int(options['port']), 
                            SSMIFactory(app_register_callback=app_register))


serviceMaker = SSMIServiceMaker()