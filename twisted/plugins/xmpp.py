from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker

from alexandria.twisted.xmpp import XMPPClient

class Options(usage.Options):
    optParameters = [
        ["username", "u", None, "XMPP username."],
        ["password", "p", None, "XMPP password."],
        ["host", "h", 'talk.google.com', "XMPP host."],
        ["port", None, 5222, "XMPP host's port."],
    ]


class XMPPServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "xmpp"
    description = "Run Alexandria over XMPP"
    options = Options
    
    def makeService(self, options):
        return XMPPClient(**options)

serviceMaker = XMPPServiceMaker()