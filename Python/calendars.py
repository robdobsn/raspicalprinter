from __future__ import print_function
import requests
from datetime import datetime

class Calendars:
	
	def printCal(self, printer, person):
		try:
			r = requests.get ('http://macallan:5077/calendar/min/7')
			calendarevents = r.json()
		except:
			printer.println ("Cannot connect to calendar")
			return
		
		lastDate = ""
		eventsPrinted = 0
		for event in calendarevents['calEvents']:
			# date, duration, summary, location, UID
			eventDate = event['eventDate']
			eventTime = event['eventTime']
			eventDatetime = datetime.strptime(eventDate+eventTime, "%Y%m%d%H:%M")
			duration = event ['duration'] 
			summary = event ['summary']
			location = event ['location']
			if lastDate != eventDate:
				if lastDate != "":
					printer.println()
					break
				printer.boldOn()
				printer.print(eventDatetime.strftime("%a") + " " + eventDatetime.strftime("%d %B"))
				if person == "":
					printer.println(" Calendar")
				else:
					printer.println(" " + person + "'s Calendar")
				printer.boldOff()
				printer.println()
				#calStr += "<b>" + anEvent[0].strftime("%a") + " (" + anEvent[0].strftime("%d %B)") + ")</b><br/>"
				lastDate = eventDate
				
			if person == "" or (summary.lower().find(person.lower()) != -1):
				strDurTimes = duration.split(":")
				durStr = (strDurTimes[0] + "day" + ("s" if strDurTimes[0] != "001" else "")) if strDurTimes[0] != "000" else (strDurTimes[1] + ":" + strDurTimes[2])
				printer.boldOn()
				printer.print(eventTime)
				printer.boldOff()
				printer.print(" (" + durStr + ") ")
				printer.boldOn()
				printer.print (summary)
				printer.boldOff()
				printer.println (" " + location)
				eventsPrinted += 1
#			calStr += anEvent[0].strftime("%H:%M") + " <small>(" + durStr + ")</small> " + summary + " " + locStr + "<br/>"
#                        print (anEvent)
#                    print(date)

#		for event in calendarevents['calEvents']:
#			print( event ['eventDate'] + ' ' + event ['eventTime'] + ' ' + event ['duration'] + ' ' + event ['location'] + ' ' + event ['summary'])

		if eventsPrinted == 0:
			printer.boldOn()
			printer.println("Nothing Doing")
			printer.boldOff()
