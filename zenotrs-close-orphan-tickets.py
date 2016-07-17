#!/usr/bin/env python
from otrs.client import GenericTicketConnector
from otrs.objects import Ticket, Article, DynamicField, Attachment

from pyzenoss.zenoss import Zenoss

import mimetypes
import argparse

parser = argparse.ArgumentParser(description='Close OTRS tickets created by zenotrs-create-ticket.py where the events have closed but the tickets remain open due to malfunction, such as temporary loss of connectivity between Zenoss and OTRS')
parser.add_argument('otrsurl', help="URL of OTRS server (ex. http://otrs.mycompany.com)")
parser.add_argument('otrsuser', help="Username of OTRS user")
parser.add_argument('otrspass', help="Password of OTRS user")
parser.add_argument('zenossurl', help="URL of Zenoss server (ex. http://zenoss.mycompany.com:8080)")
parser.add_argument('zenossuser', help="Username of Zenoss user")
parser.add_argument('zenosspass', help="Password of Zenoss user")
parser.add_argument("--queue", help="OTRS Queue for Ticket", required=True)
parser.add_argument("--ownerid", help="OTRS Owner ID number for Ticket", required=True)
parser.add_argument("--type", help="OTRS Type of Ticket", required=True)
parser.add_argument("--eventfield", help="OTRS Dynamic Field for storing Zenoss Event ID", required=True)
args = parser.parse_args()

server_uri = args.otrsurl
webservice_name = 'GenericTicketConnector'
client = GenericTicketConnector(server_uri, webservice_name)

client.user_session_register(args.otrsuser,args.otrspass)

zenoss = Zenoss(args.zenossurl, args.zenossuser, args.zenosspass)

t_ids = client.ticket_search(Queues=args.queue, OwnerIDs=args.ownerid, Types=args.type, States='new')
for t_id in t_ids:
      ticket = client.ticket_get(t_id,get_dynamic_fields=True)
      for dfield in ticket.dynamicfields():
            if dfield.Name == args.eventfield:
               eventState = zenoss.get_event_detail(dfield.Value)['event'][0]['eventState']
               print "Open Ticket #" + str(t_id) + ", event " + dfield.Value + ": Current Zenoss event state is " + eventState
               if (eventState != 'New') and (eventState != 'Acknowledged') and (eventState != 'Suppressed'):
                  a = Article(Subject='Clearing orphaned ticket', Body='Orphaned ticket detected, event closed, ticket should have been auto-closed but was not for some reason. Closing ticket.', Charset='UTF8', MimeType='text/plain', TimeUnit='1')

                  t_upd = Ticket(State='closed successful')
                  print "Orphaned ticket detected. Closing ticket..."
                  client.ticket_update(article=a, ticket=t_upd, ticket_id=t_id)
