from django.db import models
from django.utils import simplejson
import types
from datetime import timedelta, datetime

class ClientTimeLimitManager(models.Manager):
    
    TIME_LIMIT = timedelta(minutes=3)
    
    def recent(self, uuid, client_type):
        try:
            return super(ClientTimeLimitManager, self) \
                    .get_query_set() \
                    .get(uuid=uuid, 
                            client_type=client_type,
                            created_at__gte=datetime.now() - self.TIME_LIMIT,
                            active=True)
        except Client.DoesNotExist, e:
            return Client.objects.create(uuid=uuid, client_type=client_type)
        

class Client(models.Model):
    """A client that's connected"""
    uuid = models.CharField(blank=True, max_length=255)
    client_type = models.CharField(blank=True, max_length=100)
    active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ClientTimeLimitManager()
    
    class Admin:
        list_display = ('uuid','created_at', 'updated_at')
        search_fields = ('',)

    def __unicode__(self):
        return u"Client"

class Item(models.Model):
    """A session item to store"""
    client = models.ForeignKey(Client)
    key = models.CharField(blank=True, max_length=180)
    value = models.CharField(blank=True, max_length=180)
    value_type = models.CharField(null=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    DESERIALIZERS = {
        'Boolean': lambda v: v == 'True',
        'Dict': lambda v: simplejson.loads(v),
        'Float': lambda v: types.FloatType(v),
        'Int': lambda v: types.IntType(v),
        'List': lambda v: simplejson.loads(v),
        'Long': lambda v: types.LongType(v),
        'None': lambda v: None,
        'String': lambda v: types.StringType(v),
        'Tuple': lambda v: tuple(simplejson.loads(v)),
        'Unicode': lambda v: types.UnicodeType(v)
    }
    
    SERIALIZERS = {
        'Boolean': lambda v: v,
        'Dict': lambda v: simplejson.dumps(v),
        'Float': lambda v: v,
        'Int': lambda v: v,
        'List': lambda v: simplejson.dumps(v),
        'Long': lambda v: v,
        'None': lambda v: v,
        'String': lambda v: v,
        'Tuple': lambda v: simplejson.dumps(v),
        'Unicode': lambda v: v
    }
    
    class Admin:
        list_display = ('key','value','created_at')
        search_fields = ('key','value')
    
    def determine_type(self, value):
        for available_type in self.SERIALIZERS:
            klass = getattr(types,'%sType' % available_type)
            if isinstance(value, klass):
                return available_type
        return None
    
    @property
    def deserialized_value(self):
        if self.value_type:
            deserializer = self.DESERIALIZERS[self.value_type]
            return deserializer(self.value)
        return None
    
    def save(self, *args, **kwargs):
        # get the type we're trying to save, store it for deserializing
        self.value_type = self.determine_type(self.value)
        if self.value_type:
            # get the serializer
            serializer = self.SERIALIZERS[self.value_type]
            # set the value to be stored in the db
            self.value = serializer(self.value)
        return super(Item, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return u"%s (%s)" % (self.key, self.value_type)
    

