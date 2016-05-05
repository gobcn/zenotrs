ZEN-OTRS - OTRS ticket creation/update from Zenoss

1. Install these scripts on zenoss server, in folder /home/zenoss/zenotrs
2. Edit first line of scripts to change python path if desired (ex. perhaps might use zenoss python version path)
3. Make subfolder 'otrs' of the folder these scripts are in (ex. /home/zenoss/zenotrs/otrs) and install python-otrs files __init__.py, client.py, and objects.py into this folder, from this URL: https://github.com/ewsterrenburg/python-otrs/tree/master/otrs
4. Configure GenericTicketConnector in OTRS web services as per python-otrs documentation online
5. Create user zenotrs in otrs with a strong password (ex. mystrongpassword), give privileges as required for ticket creation and closure
6. Assign or create a Dynamic Field for tickets in OTRS to store the OTRS event ID, this field name will be passed as a parameter
7. In OTRS Admin->Sysconfig, under Framework, subgroup Core::Session, increase the values of AgentSessionLimit and AgentSessionPerUserLimit. This is necessary since every time a ticket is either opened or closed, a session is opened which times out after 10 minutes (by default). If a large number of zenoss events create tickets in a short period, the OTRS server can run out of free sessions with the default config and this can interfere with ticket generation and closure. This should be increased to a few thousand sessions for a busy system.
8. Add triggers in Zenoss to call scripts, Command type. Command and clear command examples shown below:

Zenoss command trigger to create ticket in OTRS (adjust as needed for your setup):

/home/zenoss/zenotrs/zenotrs-create-ticket.py --queue "NOC::Events::Network" --customer "${evt/Location}" --owner zenotrs --type "NOC Event" --eventfield TicketFreeText2 --eventid ${evt/evid} --device "${evt/device_title}" --component "${evt/component}" --severity "${evt/severityString}" --time "${evt/lastTime}" --summary ${evt/summary} --message ${evt/message} --eventurl "${urls/eventUrl}" --ackurl "${urls/ackUrl}" --closeurl "${urls/closeUrl}" --eventsurl "${urls/eventsUrl}" http://otrs.mycompany.com zenotrs mystrongpassword

Zenoss clear command trigger to close ticket in OTRS (adjust as needed for your setup):

/home/zenoss/zenotrs/zenotrs-close-ticket.py --eventfield TicketFreeText2 --eventid ${evt/evid} --device "${evt/device_title}" --component "${evt/component}" --severity "${evt/severityString}" --clearid "${evt/clearid}" --statechange "${evt/stateChange}" --clearsummary '${clearEvt/summary}' --summary ${evt/summary} --message ${evt/message} --reopenurl "${urls/reopenUrl}" http://otrs.mycompany.com zenotrs mystrongpassword



