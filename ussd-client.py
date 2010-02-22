from twisted.application import internet
from twisted.application.service import IServiceMaker

from alexandria.client import FakeUSSDClient
from examples.hivquiz import ms

client = FakeUSSDClient('console-client')

client_input = client.receive()
while client_input:
    """a blank line input cancels the while loop"""
    client.answer(client_input, ms)
    client_input = client.receive().strip()