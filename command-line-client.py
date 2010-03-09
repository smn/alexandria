#!/usr/bin/python
from twisted.application import internet
from twisted.application.service import IServiceMaker

from alexandria.client import FakeUSSDClient
from examples import devquiz

import sys

msisdn = sys.argv.pop()
if not msisdn.isdigit():
    raise Exception, "Please provide an MSDISDN such as 27761234567"


client = FakeUSSDClient(msisdn)

client_input = client.receive()
while client_input:
    """a blank line input cancels the while loop"""
    client.answer(client_input, devquiz.get_menu())
    client_input = client.receive().strip()