from zope.interface import implements
from getpass import getpass

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker

from alexandria.transport.xmpp import XMPPClient
from django.utils import importlib

class Options(usage.Options):
    optParameters = [
        ["xmpp-username", "u", None, "XMPP username.", str],
        ["xmpp-password", "p", '', "XMPP password.", str],
        ["xmpp-host", "h", 'talk.google.com', "XMPP host.", str],
        ["xmpp-port", None, 5222, "XMPP host's port.", int],
        ["menu", "m", '', 'The menu system to run', str]
    ]


class XMPPServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "xmpp"
    description = "Run Alexandria over XMPP"
    options = Options
    
    def makeService(self, options):
        if not options['xmpp-password']:
            options['xmpp-password'] = getpass('password for %s: ' % \
                                                    options['xmpp-username'])
        if not options['menu']:
            raise RuntimeError, 'please specify the menu to run with --menu='
        menu_module = importlib.import_module(options['menu'])
        menu_system = menu_module.get_menu()
        
        return XMPPClient(menu_system, username=options['xmpp-username'],
                            password=options['xmpp-password'],
                            host=options['xmpp-host'],
                            port=options['xmpp-port'])

serviceMaker = XMPPServiceMaker()