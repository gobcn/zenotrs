#!/bin/python
from otrs.client import GenericTicketConnector
from otrs.objects import Ticket, Article, DynamicField, Attachment

import mimetypes
import argparse

parser = argparse.ArgumentParser(description='Close OTRS Ticket created by zenotrs-create.ticket.py')
parser.add_argument('otrsurl', help="URL of OTRS server (ex. http://otrs.mycompany.com)")
parser.add_argument('otrsuser', help="Username of OTRS user")
parser.add_argument('otrspass', help="Password of OTRS user")
parser.add_argument("--eventfield", help="OTRS Dynamic Field for storing Zenoss Event ID", required=True)
parser.add_argument("--eventid", help="Zenoss Event ID (GUID)", required=True)
parser.add_argument("--device", help='Device event is related to', required=True)
parser.add_argument("--component", help='Component the event is related to', required=True)
parser.add_argument("--severity", help='Zenoss severity for event', required=True)
parser.add_argument("--clearid", help='Zenoss explanation for why event was cleared (ex. aging)', required=True)
parser.add_argument("--statechange", help='Time event cleared(Zenoss)', required=True)
parser.add_argument("--clearsummary", help='Summary for clear event', required=True)
parser.add_argument("--summary", help='Summary for original event', required=True)
parser.add_argument("--message", help='Event message body', required=True)
parser.add_argument("--reopenurl", help="URL to reopen event in Zenoss", required=True)
args = parser.parse_args()

server_uri = args.otrsurl
webservice_name = 'GenericTicketConnector'
client = GenericTicketConnector(server_uri, webservice_name)

client.user_session_register(args.otrsuser,args.otrspass)

subject = "[zenoss] CLEAR: " + args.device + " " + args.clearsummary
body = "Event: " + args.summary + "\n" \
     + "Cleared by: " + args.clearid + "\n" \
     + "At: " + args.statechange + "\n" \
     + "Device: " + args.device + "\n" \
     + "Component: " + args.component + "\n" \
     + "Severity: " + args.severity + "\n" \
     + "Message: \n\n" \
     + args.message + "\n\n\n" \
     + "Reopen: " + args.reopenurl

a = Article(Subject=subject, Body=body, Charset='UTF8',
            MimeType='text/plain', TimeUnit='0')
df1 = DynamicField(Name=args.eventfield, Value=args.eventid, Operator="Equals")
# t_id, t_number = client.ticket_create(t, a)
try:
   t_id = client.ticket_search(dynamic_fields=[df1])[0]
   ticket = client.ticket_get(t_id)
   client.ticket_update(article=a, ticket_id=t_id)
   # only auto-close ticket if new and owner is still zenotrs user
   if (ticket.State == "new") & (ticket.Owner == args.otrsuser):
      t_upd = Ticket(State='closed successful')
      client.ticket_update(ticket=t_upd, ticket_id=t_id)
except:
   print "Cannot update ticket - ticket with matching event id not found!"

