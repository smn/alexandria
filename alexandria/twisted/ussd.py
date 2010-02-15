from alexandria.client import Client
from examples.hivquiz import ms
import logging
from ssmi.client import (SSMI_USSD_TYPE_NEW, SSMI_USSD_TYPE_EXISTING, 
                            SSMI_USSD_TYPE_END, SSMI_USSD_TYPE_TIMEOUT)

class AlexandriaSSMIClient(Client):
    
    def __init__(self, msisdn, send_callback):
        super(AlexandriaSSMIClient, self).__init__(msisdn)
        self.msisdn = msisdn
        self.send_callback = send_callback
    
    def send(self, text):
        return self.send_callback(self.msisdn, text)
    

class SSMIService(object):
    """A Service which can be hooked into a Twisted reactor loop"""
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.clients = {}
        self.ms = ms.clone()
    
    def register_ssmi(self, ssmi_protocol):
        self.ssmi_client = ssmi_protocol
        self.ssmi_client.app_setup(username=self.username, 
                                    password=self.password,
                                    ussd_callback=self.process_ussd, 
                                    sms_callback=self.process_sms)
            
    
    def reply(self, msisdn, text):
        return self.ssmi_client.send_ussd(msisdn, text)
    
    def process_sms(self, *args):
        """Process an SMS message received in reply to an SMS we sent out."""
        pass
    
    def new_ussd_session(self, msisdn, message):
        client = self.clients.setdefault(msisdn, \
                                AlexandriaSSMIClient(msisdn, self.reply))
        client.answer(message, self.ms)
    
    def existing_ussd_session(self, msisdn, message):
        client = self.clients[msisdn]
        client.answer(message, self.ms)
    
    def timed_out_ussd_session(self, msisdn, message):
        logging.debug('%s timed out, removing client' % msisdn)
        del self.clients[msisdn]
    
    def end_ussd_session(self, msisdn, message):
        logging.debug('%s ended the session, removing client' % msisdn)
        del self.clients[msisdn]
    
    def process_ussd(self, msisdn, ussd_type, ussd_phase, message):
        if self.ssmi_client is None:
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
    

