from twisted.application import service
from twisted.words.xish import domish
from twisted.words.protocols.jabber.jid import JID
from twisted.python import usage
from wokkel import client, xmppim

from alexandria.client import Client
from alexandria.sessions.manager import SessionManager
from alexandria.sessions.backend import DBBackend

class AlexandriaXMPPClient(Client):
    
    def __init__(self, recipient, reply_callback):
        self.id = recipient
        self.reply_callback = reply_callback
        self.session_manager = SessionManager(client=self, backend=DBBackend())
        self.session_manager.restore()
    
    def send(self, message, end_of_session):
        self.reply_callback(self.id, message)
    

class MessageHandler(xmppim.MessageProtocol):
    def __init__(self, menu_system, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)
        self.menu_system = menu_system.clone()
        self.clients = {}
    
    def connectionMade(self):
        # send initial presence
        self.send(xmppim.AvailablePresence())
    
    def connectionLost(self, reason):
        print "Disconnected!"
    
    def onMessage(self, msg):
        if msg["type"] == 'chat' and hasattr(msg, "body") and msg.body:
            client = self.clients.setdefault(msg['from'], \
                                AlexandriaXMPPClient(msg['from'], self._reply))
            client.answer(str(msg.body), self.menu_system)
    
    def _reply(self, recipient, message):
        reply = domish.Element((None, "message"))
        reply["to"] = recipient
        reply["type"] = 'chat'
        reply.addElement("body", content=message)
        return self.send(reply)
    


class PresenceHandler(xmppim.PresenceProtocol):
    
    def subscribeReceived(self, presence):
        """
        Subscription request was received.

        Always grant permission to see our presence.
        """
        self.subscribed(recipient=presence.sender,
                        sender=presence.recipient)
        self.available(recipient=presence.sender,
                       status=u"I'm here",
                       sender=presence.recipient)
    
    def unsubscribeReceived(self, presence):
       """
       Unsubscription request was received.

       Always confirm unsubscription requests.
       """
       self.unsubscribed(recipient=presence.sender,
                         sender=presence.recipient)
    
    def probeReceived(self, presence):
         """
         A presence probe was received.

         Always send available presence to whoever is asking.
         """
         self.available(recipient=presence.sender,
                        status=u"I'm here",
                        sender=presence.recipient)


class RosterHandler(xmppim.RosterClientProtocol):
    
    def onRosterSet(self, item):
        print item
    
    def onRosterRemove(self, entity):
        print entity
    

class XMPPClient(client.XMPPClient):
    
    def __init__(self, menu_system, username, password, host, port):
        super(XMPPClient, self).__init__(JID(username), password, host, port)
        self.logTraffic = False
        
        # trying to figure out how to automatically accept new buddy
        # authorization requests, failing atm
        # presence_handler = PresenceHandler()
        # presence_handler.setHandlerParent(self)
        # 
        # roster_handler = RosterHandler()
        # roster_handler.setHandlerParent(self)
        
        message_handler = MessageHandler(menu_system)
        message_handler.setHandlerParent(self)
        
    
