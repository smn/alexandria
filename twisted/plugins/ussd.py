from zope.interface import implements
from getpass import getpass

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application import internet
from twisted.application.service import IServiceMaker

from alexandria.dsl.twisted.ussd import SSMIService
from ssmi import SSMIFactory
from django.utils import importlib

class Options(usage.Options):
    optParameters = [
        ["username", "u", '', "SSMI username"],
        ["password", "pw", '', "SSMI password"],
        ["host", "h", '', "SSMI host"],
        ["port", "p", '', "SSMI host's port"],
        ['menu', 'm', None, 'The menu system to run']
    ]


class SSMIServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "ussd"
    description = "Run Alexandria over USSD"
    options = Options
    
    def makeService(self, options):
        menu_module = importlib.import_module(options['menu'])
        menu_system = menu_module.get_menu()
        
        # all are mandatory, if they haven't been provided, prompt for them
        for key in options:
            if not options[key]:
                options[key] = getpass('%s: ' % key)
        
        def app_register(ssmi_protocol):
            return SSMIService(menu_system, options['username'], options['password']) \
                                .register_ssmi(ssmi_protocol)
        
        return internet.TCPClient(options['host'], int(options['port']), 
                            SSMIFactory(app_register_callback=app_register))


serviceMaker = SSMIServiceMaker()