from ssmi.client import (SSMI_USSD_TYPE_NEW, SSMI_USSD_TYPE_EXISTING, 
                            SSMI_USSD_TYPE_END, SSMI_USSD_TYPE_TIMEOUT)

class SSMIService(object):
    """A Service which can be hooked into a Twisted reactor loop"""
    def __init__(self, menu_system, username, password):
        self.menu_system = menu_system
        self.username = username
        self.password = password
        self.store = {}
    
    def register_ssmi(self, ssmi_protocol):
        self.client = ssmi_protocol
        self.client.app_setup(username=self.username, 
                                    password=self.password,
                                    ussd_callback=self.process_ussd, 
                                    sms_callback=self.process_sms)
    
    def process_sms(self, *args):
        """Process an SMS message received in reply to an SMS we sent out."""
        pass
    
    def new_ussd_session(self, msisdn, message):
        self.store.setdefault(msisdn, [])
        self.store[msisdn].append(message)
        self.client.send_ussd(msisdn, 'new!')
    
    def existing_ussd_session(self, msisdn, message):
        self.store[msisdn].append(message)
        self.client.send_ussd(msisdn, 'existing!')
    
    def timed_out_ussd_session(self, msisdn, message):
        self.store[msisdn].append(message)
        print self.store
    
    def end_ussd_session(self, msisdn, message):
        self.store[msisdn].append(message)
        print self.store
    
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
    

