from alexandria.core import coroutine
from ssmi.client import (SSMI_USSD_TYPE_NEW, SSMI_USSD_TYPE_EXISTING, 
                            SSMI_USSD_TYPE_END, SSMI_USSD_TYPE_TIMEOUT)

class SSMIClient(object):
    def __init__(self, msisdn, ssmi_client):
        self.msisdn = msisdn
        self.ssmi_client = ssmi_client
        self.store = {}
        self.step = 0
        self.previous_answer = ''
        self.waiting_for_answer = False
    
    def process(self, menu_system):
        for step, coroutine, question in menu_system.run(start_at=self.step):
            # question might be None if for some reason the coroutine turns
            # out not to need any user info
            if question:
                answer = yield self.connection().send(question)
                print 'got answer', answer
                validated_answer = coroutine.send(answer)
                yield step, coroutine, question, validated_answer
            else:
                yield step, coroutine, question, None


    @coroutine
    def connection(self):
        while True:
            output = yield
            print 'sending to phone:', output
            self.ssmi_client.send_ussd(output, self.msisdn)
            self.waiting_for_answer = True
            print 'waiting for answer from phone, yielding'
            response = (yield)
            print 'got response', response
            yield response
            self.waiting_for_answer = False
    

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
    
    def send_and_yield_with_reply(self, msisdn, msg):
        self.client.send_ussd(msisdn, msg)
    
    def get_client_for(self, msisdn):
        return self.store.setdefault(msisdn, SSMIClient(msisdn, self.client))
    
    def new_ussd_session(self, msisdn, message):
        self.next_step().send((msisdn, message))
    
    def existing_ussd_session(self, msisdn, message):
        self.next_step().send((msisdn, message))
    
    @coroutine
    def next_step(self):
        while True:
            msisdn, message = yield
            print '>>> %s: %s' % (msisdn, message)
            client = self.get_client_for(msisdn)
            if client.waiting_for_answer:
                print "received message from client", message
                client.connection().send(message)
            for step, coroutine, question, answer in client.process(self.menu_system):
                client.step = step + 1
    
    def timed_out_ussd_session(self, msisdn, message):
        print msisdn, 'timed out'
    
    def end_ussd_session(self, msisdn, message):
        print msisdn, 'ended with message', message
    
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
    

