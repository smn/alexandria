from zope.interface import implements
from getpass import getpass

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker

from alexandria.dsl.twisted.xmpp import XMPPClient

class Options(usage.Options):
    optParameters = [
        ["username", "u", None, "XMPP username."],
        ["password", "p", '', "XMPP password."],
        ["host", "h", 'talk.google.com', "XMPP host."],
        ["port", None, 5222, "XMPP host's port."],
    ]


class XMPPServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "xmpp"
    description = "Run Alexandria over XMPP"
    options = Options
    
    def makeService(self, options):
        if 'p' not in options:
            options['password'] = getpass('password for %s: ' % options['username'])
        return XMPPClient(**options)

serviceMaker = XMPPServiceMaker()