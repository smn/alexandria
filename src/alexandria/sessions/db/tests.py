from django.test import TestCase
from models import Client, ClientTimeLimitManager
from datetime import *

class ClientTimeLimitTestCase(TestCase):
    
    def setUp(self):
        self.kwargs = {
            "uuid": "uuid", 
            "client_type": "TestClient"
        }
    
    def test_recent_expiry(self):
        """
        recent() should never return a client that's older than the given
        TIME_LIMIT
        """
        client = Client.objects.create(**self.kwargs)
        client.created_at = datetime.now() - (ClientTimeLimitManager.TIME_LIMIT * 2)
        client.save()
        
        self.assertNotEquals(client.pk, Client.objects.recent(**self.kwargs).pk)
    
    def test_recent(self):
        """
        recent() should always return the client if it's still within the 
        given TIME_LIMIT
        """
        client = Client.objects.create(**self.kwargs)
        client.created_at = datetime.now() - timedelta(seconds=1)
        client.save()
        
        self.assertEquals(client.pk, Client.objects.recent(**self.kwargs).pk)
    

class ClientTestCase(TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_repr(self):
        c = Client()
        self.assertEquals(unicode(c), u"Client")
    
