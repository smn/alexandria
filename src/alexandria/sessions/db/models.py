from django.db import models
from django.utils import simplejson
import types
from datetime import timedelta, datetime

class ClientTimeLimitManager(models.Manager):
    
    TIME_LIMIT = timedelta(minutes=15)
    
    def recent(self, uuid, client_type):
        """
        Returns a client for the given UUID and client type that has a 
        session of no older than `TIME_LIMIT`.
        
        If none exists then it'll create a new client for a new session.
        """
        try:
            client = super(ClientTimeLimitManager, self) \
                    .get_query_set() \
                    .get(uuid=uuid, 
                            client_type=client_type,
                            updated_at__gte=datetime.now() - self.TIME_LIMIT,
                            # active=True)
                            )
            if not client.active:
                client.item_set.filter(key='previous_index').delete()
                client.active=True
                client.save()
            return client
        except Client.DoesNotExist, e:
            return Client.objects.create(uuid=uuid, client_type=client_type)
        

class Client(models.Model):
    """
    A client that's connected
    """
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

class ItemException(Exception): pass

class Item(models.Model):
    """A session item to store"""
    client = models.ForeignKey(Client)
    key = models.CharField(blank=True, max_length=180)
    value = models.CharField(blank=True, max_length=180)
    value_type = models.CharField(null=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # FIXME:    Ooh my, does this a lot better than we do, I shouldn't be
    #           writing this stuff.
    DESERIALIZERS = [
        ('Boolean', lambda v: v == 'True'), 
        ('Dict', lambda v: simplejson.loads(v)), 
        ('Float', lambda v: types.FloatType(v)), 
        ('Int', lambda v: types.IntType(v)), 
        ('List', lambda v: simplejson.loads(v)), 
        ('Long', lambda v: types.LongType(v)), 
        ('None', lambda v: None), 
        ('String', lambda v: types.StringType(v)), 
        ('Tuple', lambda v: tuple(simplejson.loads(v))), 
        ('Unicode', lambda v: types.UnicodeType(v)), 
    ]
    
    # the order is importance since python things True == 1 causing
    # a mixup of BooleanType and IntType, by checking for the BooleanType
    # first we avoid that problem.
    SERIALIZERS = [
        ('Boolean', lambda v: v), 
        ('Dict', lambda v: simplejson.dumps(v)), 
        ('Float', lambda v: v), 
        ('Int', lambda v: v), 
        ('List', lambda v: simplejson.dumps(v)), 
        ('Long', lambda v: v), 
        ('None', lambda v: v), 
        ('String', lambda v: v), 
        ('Tuple', lambda v: simplejson.dumps(v)), 
        ('Unicode', lambda v: v)
    ]
    
    class Admin:
        list_display = ('key','value','created_at')
        search_fields = ('key','value')
    
    def determine_type(self, value):
        """
        Try and determine the type for the given value, it does this by
        looping over the available SERIALIZERS and returning the type if
        the given value is of the given type.
        
        >>> item = Item()
        >>> item.determine_type(True)
        'Boolean'
        >>> item.determine_type({'key': 'value'})
        'Dict'
        >>> item.determine_type(1.0)
        'Float'
        >>> item.determine_type(1)
        'Int'
        >>> item.determine_type([1,2,3])
        'List'
        >>> item.determine_type(1234L)
        'Long'
        >>> item.determine_type(None)
        'None'
        >>> item.determine_type("String")
        'String'
        >>> item.determine_type((1,2,3,4))
        'Tuple'
        >>> item.determine_type(u'Unicode')
        'Unicode'
        >>> # unknown types should return None
        >>> item.determine_type(Exception)
        >>>
        
        """
        for available_type, _ in self.SERIALIZERS:
            klass = getattr(types,'%sType' % available_type)
            if isinstance(value, klass):
                return available_type
        return None
    
    @property
    def deserialized_value(self):
        """
        Returns the deserialized value of the value states been saved in
        serialized state in the database.
        
        >>> item = Item(client=Client.objects.create())
        >>> item.key = "1"
        >>> item.value = {'foo':'bar'}
        >>> item.save()
        >>>
        >>> pk = item.pk
        >>> item = Item.objects.get(pk=pk)
        >>> item.deserialized_value
        {u'foo': u'bar'}
        >>>
        >>> item = Item()
        >>> item.value_type = 'NonExistent'
        >>> try: 
        ...     item.deserialized_value
        ... except ItemException, e: 
        ...     print e
        ... 
        value_type unknown, unable to deserialize
        >>> 
        
        """
        if self.value_type:
            for deserializer_type, deserializer in self.DESERIALIZERS:
                if self.value_type == deserializer_type:
                    return deserializer(self.value)
        raise ItemException, 'value_type unknown, unable to deserialize'
    
    def save(self, *args, **kwargs):
        """
        Serialize the data before saving it to the database. 
        
        FIXME:  This is buggy since the data and type stored in the 'value' 
                variable will change before and after a save. This is a 
                horrible side effect.
        
        FIXME:  Use a pre_save signal instead
        """
        # get the type we're trying to save, store it for deserializing
        self.value_type = self.determine_type(self.value)
        if self.value_type:
            # get the serializer
            for serializer_type, serializer in self.SERIALIZERS:
                if self.value_type == serializer_type:
                    # set the value to be stored in the db
                    self.value = serializer(self.value)
                    break
        return super(Item, self).save(*args, **kwargs)
    
    def __unicode__(self):
        """
        >>> item = Item()
        >>> item.client = Client.objects.create()
        >>> item.key = "foo"
        >>> item.value = "bar"
        >>> item.save()
        >>> unicode(item)
        u'foo (String)'
        >>>
        """
        return u"%s (%s)" % (self.key, self.value_type)
    

