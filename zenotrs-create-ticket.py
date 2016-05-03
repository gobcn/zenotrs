#!/bin/python
from otrs.client import GenericTicketConnector
from otrs.objects import Ticket, Article, DynamicField, Attachment

import mimetypes
import argparse

parser = argparse.ArgumentParser(description='Create OTRS Ticket from Zenoss event.')
parser.add_argument('otrsurl', help="URL of OTRS server (ex. http://otrs.mycompany.com)")
parser.add_argument('otrsuser', help="Username of OTRS user")
parser.add_argument('otrspass', help="Password of OTRS user")
parser.add_argument("--queue", help="OTRS Queue for Ticket", required=True)
parser.add_argument("--customer", help="OTRS Customer user for Ticket", required=True)
parser.add_argument("--owner", help="OTRS Owner for Ticket", required=True)
parser.add_argument("--type", help="OTRS Type of Ticket", required=True)
parser.add_argument("--eventfield", help="OTRS Dynamic Field for storing Zenoss Event ID", required=True)
parser.add_argument("--eventid", help="Zenoss Event ID (GUID)", required=True)
parser.add_argument("--device", help='Device event is related to', required=True)
parser.add_argument("--component", help='Component the event is related to', required=True)
parser.add_argument("--severity", help='Zenoss severity for event', required=True)
parser.add_argument("--time", help='Time of event(Zenoss)', required=True)
parser.add_argument("--summary", help='Event summary', required=True)
parser.add_argument("--message", help='Event message body', required=True)
parser.add_argument("--eventurl", help="URL to view event detail in Zenoss", required=True)
parser.add_argument("--ackurl", help="URL to acknowledge event in Zenoss", required=True)
parser.add_argument("--closeurl", help="URL to clear event in Zenoss", required=True)
parser.add_argument("--eventsurl", help="URL to view all events for device in Zenoss", required=True)
args = parser.parse_args()

server_uri = args.otrsurl
webservice_name = 'GenericTicketConnector'
client = GenericTicketConnector(server_uri, webservice_name)

client.user_session_register(args.otrsuser,args.otrspass)

subject = "[zenoss] " + args.device + " " + args.summary
body = "Device: " + args.device + "\n" \
     + "Component: " + args.component + "\n" \
     + "Severity: " + args.severity + "\n" \
     + "Time: " + args.time + "\n\n" \
     + "Message: \n\n" \
     + args.message + "\n\n\n" \
     + "Event Detail: " + args.eventurl + "\n" \
     + "Acknowledge: " + args.ackurl + "\n" \
     + "Close: " + args.closeurl + "\n" \
     + "Device Events " + args.eventsurl 
if (args.severity == 'Critical'):
   priority='5 very high'
elif (args.severity == 'Error'):
   priority='4 high'
else:
   priority='3 normal'

t = Ticket(State='new', Priority=priority, Queue=args.queue,
           Owner=args.owner, Title=subject, CustomerUser=args.customer,
           Type=args.type)
a = Article(Subject=subject, Body=body, Charset='UTF8',
            MimeType='text/plain', TimeUnit='0')
df1 = DynamicField(Name=args.eventfield, Value=args.eventid)
t_id, t_number = client.ticket_create(t, a, [df1])
