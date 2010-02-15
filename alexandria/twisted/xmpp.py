from twisted.application import service
from twisted.words.xish import domish
from twisted.words.protocols.jabber.jid import JID
from twisted.python import usage
from wokkel import client, xmppim

from alexandria.client import Client
from examples.hivquiz import ms

class AlexandriaXMPPClient(Client):
    
    def __init__(self, recipient, reply_callback):
        self.recipient = recipient
        self.reply_callback = reply_callback
    
    def send(self, message):
        self.reply_callback(self.recipient, message)
    

class MessageHandler(xmppim.MessageProtocol):
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)
        self.ms = ms.clone()
        self.clients = {}
    
    def connectionMade(self):
        # send initial presence
        self.send(xmppim.AvailablePresence())
    
    def connectionLost(self, reason):
        print "Disconnected!"
    
    def onMessage(self, msg):
        if msg["type"] == 'chat' and hasattr(msg, "body"):
            client = self.clients.setdefault(msg['from'], \
                                AlexandriaXMPPClient(msg['from'], self._reply))
            client.answer(str(msg.body), self.ms)
    
    def _reply(self, recipient, message):
        reply = domish.Element((None, "message"))
        reply["to"] = recipient
        reply["type"] = 'chat'
        reply.addElement("body", content=message)
        return self.send(reply)
    

class XMPPClient(client.XMPPClient):
    
    def __init__(self, username, password, host, port):
        super(XMPPClient, self).__init__(JID(username), password, host, port)
        # self.logTraffic = True
        
        message_handler = MessageHandler()
        message_handler.setHandlerParent(self)
    
