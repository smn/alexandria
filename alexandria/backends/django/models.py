from django.db import models

class Client(models.Model):
    """A client that's connected"""
    uuid = models.CharField(blank=True, max_length=255)
    client_type = models.CharField(blank=True, max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Admin:
        list_display = ('key','value','created_at')
        search_fields = ('key','value')

    def __unicode__(self):
        return u"%s" % key


