from twisted.application import service
from twisted.words.xish import domish
from twisted.words.protocols.jabber.jid import JID
from wokkel import client, xmppim

import sys

jid = JID(sys.argv[1])
password = sys.argv[2]

application = service.Application('XMPP client')
xmppClient = client.XMPPClient(jid, password, host='talk.google.com')
xmppClient.logTraffic = True
xmppClient.setServiceParent(application)

# presence = xmppim.PresenceClientProtocol()
# presence.setHandlerParent(xmppClient)
# presence.available()

from alexandria.client import Client
from hivquiz import ms

class XMPPClient(Client):
    
    def __init__(self, to, _from, message_handler):
        self.to = to
        self._from = _from
        self.message_handler = message_handler
    
    def send(self, message):
        reply = domish.Element((None, "message"))
        reply["to"] = self._from
        reply["type"] = 'chat'
        reply.addElement("body", content=message)
        self.message_handler.send(reply)

class MessageHandler(xmppim.MessageProtocol):
    
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)
        self.ms = ms.clone()
        self.clients = {}
    
    def connectionMade(self):
        print "Connected!"

        # send initial presence
        self.send(xmppim.AvailablePresence())

    def connectionLost(self, reason):
        print "Disconnected!"
    
    def onMessage(self, msg):
        if msg["type"] == 'chat' and hasattr(msg, "body"):
            client = self.clients.setdefault(msg['from'], \
                                    XMPPClient(msg['to'], msg['from'], self))
            client.answer(str(msg.body), ms)
            # reply = domish.Element((None, "message"))
            # reply["to"] = msg["from"]
            # reply["type"] = 'chat'
            # reply.addElement("body", content="echo: " + str(msg.body))
            
            # 
            # 
            # self.send(reply)
    
message = MessageHandler()
message.setHandlerParent(xmppClient)
