from zope.interface import implements
from getpass import getpass

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application import internet
from twisted.application.service import IServiceMaker

from alexandria.transport.ussd import SSMIService
from ssmi import SSMIFactory
from django.utils import importlib

class Options(usage.Options):
    optParameters = [
        ["ssmi-username", "u", '', "SSMI username", str],
        ["ssmi-password", "pw", '', "SSMI password", str],
        ["ssmi-host", "h", '', "SSMI host"],
        ["ssmi-port", "p", '', "SSMI host's port", int],
        ['menu', 'm', '', 'The menu system to run', str]
    ]


class SSMIServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "ussd"
    description = "Run Alexandria over USSD"
    options = Options
    
    def makeService(self, options):
        if not options['menu']:
            raise RuntimeError, 'please specify the menu to run with --menu='
        menu_module = importlib.import_module(options['menu'])
        menu_system = menu_module.get_menu()
        
        # all are mandatory, if they haven't been provided, prompt for them
        for key in options:
            if not options[key]:
                options[key] = getpass('%s: ' % key)
        
        def app_register(ssmi_protocol):
            return SSMIService(menu_system, options['ssmi-username'], 
                                            options['ssmi-password']) \
                                            .register_ssmi(ssmi_protocol)
        
        return internet.TCPClient(options['ssmi-host'], int(options['ssmi-port']), 
                            SSMIFactory(app_register_callback=app_register))


serviceMaker = SSMIServiceMaker()