from alexandria.core import coroutine
from alexandria.client import Client
from hivquiz import ms
from ssmi.client import (SSMI_USSD_TYPE_NEW, SSMI_USSD_TYPE_EXISTING, 
                            SSMI_USSD_TYPE_END, SSMI_USSD_TYPE_TIMEOUT)

class SSMIClient(Client):
    
    def __init__(self, msisdn, ssmi_client):
        self.ssmi_client = ssmi_client
        self.store = {}
        super(self, SSMIClient).__init__(msisdn)
    
    def send(self, text):
        return self.ssmi_client.send_ussd(self.id, text)
    
    

class SSMIService(object):
    """A Service which can be hooked into a Twisted reactor loop"""
    def __init__(self, menu_system, username, password):
        self.menu_system = menu_system
        self.username = username
        self.password = password
        self.store = {}
        self.clients = {}
        self.ms = ms.clone()
    
    def register_ssmi(self, ssmi_protocol):
        self.ssmi_client = ssmi_protocol
        self.ssmi_client.app_setup(username=self.username, 
                                    password=self.password,
                                    ussd_callback=self.process_ussd, 
                                    sms_callback=self.process_sms)
            
    
    def process_sms(self, *args):
        """Process an SMS message received in reply to an SMS we sent out."""
        pass
    
    def new_ussd_session(self, msisdn, message):
        client = self.clients.setdefault(msisdn, SSMIClient(msisdn, self.ssmi_client))
        client.answer(message, ms)
    
    def existing_ussd_session(self, msisdn, message):
        client = self.clients[msisdn]
        client.answer(message, ms)
    
    def timed_out_ussd_session(self, msisdn, message):
        logging.debug('%s timed out' % msisdn)
        self.clients.remove(msisdn)
    
    def end_ussd_session(self, msisdn, message):
        logging.debug('%s ended the session' % msisdn)
        self.clients.remove(msisdn)
    
    def process_ussd(self, msisdn, ussd_type, ussd_phase, message):
        if self.client is None:
            log.err('FATAL: client not registered')
            return
        
        routes = {
            SSMI_USSD_TYPE_NEW: self.new_ussd_session,
            SSMI_USSD_TYPE_EXISTING: self.existing_ussd_session,
            SSMI_USSD_TYPE_TIMEOUT: self.timed_out_ussd_session,
            SSMI_USSD_TYPE_END: self.end_ussd_session
        }
        
        handler = routes[ussd_type]
        if handler:
            handler(msisdn, message)
        else:
            log.err('FATAL: No handler available for ussd type %s' % ussd_type)
    

