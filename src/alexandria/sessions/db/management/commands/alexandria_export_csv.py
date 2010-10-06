from django.core.management.base import BaseCommand, CommandError
from alexandria.sessions.db.models import Client, Item
from optparse import make_option
import sys, csv

def values_for(client, keys):
    values = []
    for key in keys:
        try:
            item = client.item_set.get(key=key)
            values.append(item.deserialized_value)
        except Item.DoesNotExist, e:
            values.append(None)
    return values

class Command(BaseCommand):
    help = 'Export Alexandria session data as a CSV file'
    
    def handle(self, *args, **options):
        ITEM_KEYS = list(set(i.key for i in Item.objects.all()))
        clients = Client.objects.all()
        writer = csv.writer(sys.stdout)
        writer.writerow([
                'UUID',
                'TYPE',
                'SESSION FINISHED',
                'CREATED AT',
                'UPDATED AT'
            # add the key's from the Item list
            ] + ITEM_KEYS)
        
        for client in clients:
            writer.writerow([
                client.uuid,
                client.client_type,
                not client.active,
                client.created_at,
                client.updated_at
            ] + values_for(client, ITEM_KEYS))
        