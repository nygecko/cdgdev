#!python
# -*- coding: utf-8 -*-
import os
import logging
logging.basicConfig(filename='cdgdev.log',level=logging.DEBUG)
current_dir = os.path.dirname(os.path.abspath(__file__))
root = current_dir

import cherrypy
import csv
import re
import urllib
##import win32serviceutil
##import win32service
import pymongo
import codecs
import json
from bson import json_util
from bson import ObjectId
from cherrypy.lib.static import serve_file

# MongoDB initialization
client = pymongo.MongoClient('localhost', 27017)
db = client.cdgdevdb

# some useful definitions
day = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
month = ['Placeholder', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
columns = ['objid', 'date', 'title', 'description', 'message', 'bizunit', 'tech', 'status', 'event', 'contact', 'link', 'notes']
bizunittypes = ['', 'BU1', 'BU2', 'BU3', 'BU4', 'BU5']
statustypes = ['', 'IDEA', 'WIP', 'DONE']

class Root:

	# user login
	@cherrypy.expose
	def login(self, userName, userPswd):
		ucUserName = userName.upper()
		ucPswd = userPswd.upper()
		#print (" %s %s " %(userName, userPswd))
		# check for admin users
		if ((ucUserName == 'ADMIN') and (ucPswd == 'CDGDEV')):
			cherrypy.session['login'] = 'ADMIN'
			return open(os.path.join(current_dir, u'adminQuery.html'))
		else:
			# check for non-admin users
			if (ucUserName.isalpha()):
				ucUserName = ucUserName
			else:
				ucUserName = re.sub(r'[\W\d]', "", ucUserName.strip())
			# WIP - add code to authenticate non-admin users then send them to userQuery.html
			#return open(os.path.join(current_dir, u'userQuery.html'))

	# convert dict to unicode for use in url
	def unicodeDict(self, myDict):
		for i, j in myDict.items():
			myDict[i] = j.encode('utf-8')
		#    print ("%s %s" %(i, myDict[i]))
		return myDict
	# download db contents into csv file
	@cherrypy.expose        
	def putCsv(self):
		return open(os.path.join(current_dir, u'putCsv.html'))

	@cherrypy.expose
	def putFile(self):
		fileName=os.path.join(current_dir, u'cdgdevexport.csv')
		logging.info('downloading existing records into filename %s', fileName)
		#print ("downloading existing records into filename %s" %fileName)
		recordCount = 0
		dbQuery = ({})
		userFile = codecs.open(fileName, encoding='utf-8', mode='w')
		userFile.write('objid, date, title, description, message, bizunit, tech, status, event, contact, link, notes\n')
		for item in db.cdgdevData.find(dbQuery):
			recordCount += 1
			objid = item['objid']
			date = item['date']
			title = item['title']
			description = item['description']
			message = item['message']
			bizunit = str(item['bizunit']).strip()
			if (not bizunit):
				bizunit = '0'
			bizunit = bizunittypes[int(bizunit)]
			tech = item['tech']
			status = str(item['status']).strip()
			if (not status):
				status = '0'
			status = statustypes[int(status)]
			event = item['event']
			contact = item['contact']
			link = item['link']
			notes = item['notes']
			userFile.write(objid + ',' + date + ',' + title + ',' + description + ',' + message + ',' + bizunit + ',' + tech + ',' + status + ',' + event + ',' + contact + ',' + link + ',' + notes + '\n')
		userFile.close()
		logging.info('Export of Existing Records Completed. Exported %d records into %s', recordCount, fileName)
		#print ("exported %d records into filename %s" %(recordCount, fileName))
		return serve_file(fileName, "application/x-download", "attachment")

	# upload csv contents into db
	@cherrypy.expose        
	def getCsv(self):
		return open(os.path.join(current_dir, u'getCsv.html'))

	@cherrypy.expose
	def getFile(self, fileName):
		logging.info('upload multiple records from filename %s', fileName)
		#print ("uploading records from filename %s" %fileName)
		page="<!DOCTYPE html>"
		page+="<html> <head>"
		page+="<meta name='viewport' content='width=device-width'>"
		page+="<title>GetFile</title>"
		page+="<link rel='stylesheet' type='text/css' href='/css/style.css'></link>"
		page+="<script type='text/javascript' src='/js/test.js'></script>"
		page+="</head>"
		page+="<div class='centerOutput'>"
		page+="<body>"
		page+="<section><br><header><h2>File</h2></header>"
		fullFileName = fileName=os.path.join(current_dir, fileName)
		page+="<p>FileName: %s </p>" %fullFileName
		userFile = open(fullFileName, 'r')
		countTotRecs = 0
		countAddRecs = 0
		countUpdRecs = 0
		countInvRecs = 0
		firstRec = True
		sizeOfCursor = 0
		for line in userFile:
			# skip 1st line of column headings
			if firstRec:
				firstRec = False
				continue
			countTotRecs = countTotRecs + 1
			#print ("<p>Line from File: %s </p>" %line)
			dataFields = line.split(',')
			numFields = len(dataFields)
			lastFieldIndex = numFields-1
			#print ("numfields %d" %numFields)
			if (numFields != (len(columns))):
				countInvRecs = countInvRecs + 1
				logging.warning('ERROR: incorrect number of fields in record %d', countTotRecs)
				#print ("ERROR incorrect number of fields in record %d" %countTotRecs)
			else:
				#print ("objid: %s" %dataFields[0])
				dataFields[lastFieldIndex] = re.sub(r'[\"]', "", dataFields[lastFieldIndex].rstrip())
				if (dataFields[5] in bizunittypes):
					bizunit = bizunittypes.index(dataFields[5])
				else:
					bizunit = '0'
				if (dataFields[7] in statustypes):
					status = statustypes.index(dataFields[7])
				else:
					status = '0'
				if (dataFields[0] == ''):
					sizeOfCursor = 0
				else:
					sizeOfCursor = db.cdgdevData.find( { '_id' : ObjectId(dataFields[0]) } ).count()
				if (sizeOfCursor == 0):
					countAddRecs = countAddRecs + 1
					logging.info('added record %d', countTotRecs)
					#print ("Record #%d: NEW - no files found - inserting new record" %countTotRecs)
					objid = str(ObjectId())
					#print ("objid: %s" %objid)
					j = { 'objid' : objid, 'date' : dataFields[1], 'title' : dataFields[2], 'description' : dataFields[3], 'message' : dataFields[4], 'bizunit' : bizunit, 'tech' : dataFields[6], 'status' : status, 'event' : dataFields[8], 'contact' : dataFields[9], 'link' : dataFields[10], 'notes' : dataFields[11] }
					db.cdgdevData.insert( j )
				else:
					countUpdRecs = countUpdRecs + 1
					logging.info('updated record %d', countTotRecs)
					#print ("Record #%d: YAY - record found - updating data" %countTotRecs)
					db.cdgdevData.update( { "_id" : ObjectId(dataFields[0])}, { 'objid' : dataFields[0], 'date' : dataFields[1], 'title' : dataFields[2], 'description' : dataFields[3], 'message' : dataFields[4], 'bizunit' : bizunit, 'tech' : dataFields[6], 'status' : status, 'event' : dataFields[8], 'contact' : dataFields[9], 'link' : dataFields[10], 'notes' : dataFields[11] }, upsert=True, multi=False )  
		userFile.close()
		page+="<p>File Upload Completed.<p>"
		logging.info('File Upload Completed. Processed %d records: Added %d records and updated %d records', countTotRecs, countAddRecs, countUpdRecs)
		page+="<p>%d records processed: %d records added, %d records updated<p>" %(countTotRecs, countAddRecs, countUpdRecs)
		page+="<p>%d records were not formatted correctly<p>" %(countInvRecs)
		page+="</section><br>"
		page+="<footer><hr><p><a href='/'>HOME</a></p><p>&copy; 2018.  All rights reserved.</p></footer>"
		page+="</div>"
		page+="</body></html>"
		return page   

	# search demos by key fields
	@cherrypy.expose
	def getData(self, searchtitle, searchdescription, searchmessage, searchtech):
		#print ("%s %s %s %s" %(searchtitle, searchdescription, searchmessage, searchtech))
		dbsearchtitle = re.sub(r'[\W]', "", searchtitle.strip())
		dbsearchdescription = re.sub(r'[\W]', "", searchdescription.strip())
		dbsearchmessage = re.sub(r'[\W]', "", searchmessage.strip())
		dbsearchtech = re.sub(r'[\W]', "", searchtech.strip())
		currentUser = cherrypy.session['login']
		invalidQuery = False
		dbQuery = ({})
		if not(dbsearchtitle, dbsearchdescription, dbsearchmessage, dbsearchtech):
			invalidQuery = True
		if dbsearchtitle:
			dbQuery['title'] = {'$regex': dbsearchtitle, '$options': '-i'}
		if dbsearchdescription:
			dbQuery['description'] = {'$regex': dbsearchdescription, '$options': '-i'}
		if dbsearchmessage:
			dbQuery['message'] = {'$regex': dbsearchmessage, '$options': '-i'}
		if dbsearchtech:
			dbQuery['tech'] = {'$regex': dbsearchtech, '$options': '-i'}
		#print ("%s %s %s %s" %(searchtitle, searchdescription, searchmessage, searchtech))
		#print ("%s %s %s %s" %(dbsearchtitle, dbsearchdescription, dbsearchmessage, dbsearchtech))
		# DB query
		page="<!DOCTYPE html>"
		page+="<html> <head>"
		page+="<meta name='viewport' content='width=device-width'>"
		page+="<title>Demo Results</title>"
		page+="<link rel='stylesheet' type='text/css' href='/css/style.css'></link>"
		page+="<script type='text/javascript' src='/js/test.js'></script>"
		page+="</head>"
		page+="<body>"
		page+="<div class='centerOutput'>"
		page+="<header><h2>Demo Results</h2></header>"
		if (invalidQuery):
			page+="<br>Invalid Query: missing search parameters"
			page+="<footer><hr><p><a href='/newSearch'>New Search</a></p><p><a href='/'>HOME</a></p><p>&copy; 2018.  All rights reserved.</p></footer>"
			page+="</div>"
			page+="</body></html>"
			return page
		page+="<br>Results for %s %s %s %s:" %(searchtitle, searchdescription, searchmessage, searchtech)
		page+="<hr>"
		objid = ''
		date = ''
		title = ''
		description = ''
		message = ''
		bizunit = '0'
		tech = ''
		status = '0'
		event = ''
		contact = ''
		link = ''
		notes = ''
		recordCount = 0
		page+="<ul class='a'>"
		page+="<li class='a'>"
		page+="<ul class='b'>"
		page+="<li class='b'>&nbsp;Title&nbsp;</li>"
		page+="<li class='c'>&nbsp;Description&nbsp;</li>"
		page+="<li class='d'>&nbsp;Messages&nbsp;</li>"
		page+="<li class='b'>&nbsp;Technologies&nbsp;</li>"
		page+="</ul class='b'>"
		page+="</li class='a'>"
		page+="<br>"
		for item in db.cdgdevData.find(dbQuery):
			#print(item)
			recordCount += 1
			objid = item['objid']
			date = item['date']
			title = item['title']
			description = item['description']
			message = item['message']
			bizunit = str(item['bizunit']).strip()
			if (not bizunit):
				bizunit = '0'
			tech = item['tech']
			status = str(item['status']).strip()
			if (not status):
				status = '0'
			event = item['event']
			contact = item['contact']
			link = item['link']
			notes = item['notes']
			page+="<li class='a'>"
			page+="<ul class='b'>"
			urlDict = {'field0' : objid, 'field1' : date, 'field2' : title, 'field3' : description, 'field4' : message, 'field5' : bizunit, 'field6' : tech, 'field7' : status, 'field8' : event, 'field9' : contact, 'field10' : link, 'field11' : notes }
			uUrlDict = self.unicodeDict(urlDict)
			hrefStr = '/editData/?' + urllib.parse.urlencode(uUrlDict)
			page+="<a href='"+hrefStr+"'>"
			page+="<li class='b'>&nbsp;%s&nbsp;</li>" %title
			page+="<li class='c'>&nbsp;%s&nbsp;</li>" %description
			page+="<li class='d'>&nbsp;%s&nbsp;</li>" %message
			page+="<li class='b'>&nbsp;%s&nbsp;</li>" %tech
			page+="</ul class='b'>"
			page+="</li class='a'>"
			page+="<br>"
		page+="</ul class='a'>"
		if (recordCount==0):
			page+="<br>No demos found</br>"
		emptyfield = ''
		objid = str(ObjectId())
		#print("objectid %s" %objid)
		urlDict = {'field0' : objid, 'field1' : emptyfield, 'field2' : searchtitle, 'field3' : searchdescription, 'field4' : searchmessage, 'field5' : '0', 'field6' : searchtech, 'field7' : '0', 'field8' : emptyfield, 'field9' : emptyfield, 'field10' : emptyfield, 'field11' : emptyfield }
		uUrlDict = self.unicodeDict(urlDict)
		hrefStr = '/editData/?' + urllib.parse.urlencode(uUrlDict)
		page+="<footer><hr><p><a href='"+hrefStr+"'>Add Demo</a></p><p><a href='/newSearch'>New Search</a></p><p><a href='/'>HOME</a></p><p>&copy; 2018.  All rights reserved.</p></footer>"
		page+="</div>"
		page+="</body></html>"
		return page

	# get edited data record from user
	@cherrypy.expose
	def editData(self, field0, field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11):
		#print ("%s %s %s %s %s %s %s %s %s %s %s %s:" %(field0, field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11))
		currentUser = cherrypy.session['login']
		# DB query
		page="<!DOCTYPE html>"
		page+="<html> <head>"
		page+="<meta name='viewport' content='width=device-width'>"
		page+="<title>Demo Edits</title>"
		page+="<link rel='stylesheet' type='text/css' href='/css/style.css'></link>"
		page+="<script type='text/javascript' src='/js/test.js'></script>"
		page+="</head>"
		page+="<body>"
		page+="<div class='centerOutput'>"
		page+="<header><h2>Demo Edits</h2></header>"
		page+="<p>Enter demo details:</p>"
		# make changes immediately if admin else send request for change via email
		if (currentUser == 'ADMIN'):
			page+="<form method='post' name='updateForm' action='/confirmData/'>"
		else:
			page+="<form method='post' name='updateForm' action='mailto:test@example.com;?Subject=Update%20Data%20Request' enctype='text/plain'>"
		page+="<datalist id='bizunittype'>"
		page+="<option value='BU1'>"
		page+="<option value='BU2'>"
		page+="<option value='BU3'>"
		page+="<option value='BU4'>"
		page+="<option value='BU5'>"
		page+="</datalist>"
		page+="<datalist id='statustype'>"
		page+="<option value='IDEA'>"
		page+="<option value='WIP'>"
		page+="<option value='DONE'>"
		page+="</datalist>"
		page+="<ul class='a'>"
		page+="<li class='a'>"
		page+="<ul class='b'>"
		page+="<li class='b'>"
		# don't display objid associated with record
		#page+="<label for='field0'>ObjId</label><br />"
		page+="<label for='field0'></label><br />"
		page+="<input type='text' name='field0' id='field0' value='"+field0+"' placeholder='"+field0+"' readonly hidden><br />"
		page+="</li>"
		page+="</ul class='b'>"
		page+="</li class='a'>"
		page+="<li class='a'>"
		page+="<ul class='b'>"
		page+="<li class='b'>"
		page+="<label for='field1'>Date</label><br />"
		page+="<input type='text' name='field1' id='field1' value='"+field1+"' placeholder='"+field1+"' autofocus><br />"
		page+="</li>"
		page+="<li class='b'>"
		page+="<label for='field2'>Title</label><br />"
		page+="<input type='text' name='field2' id='field2' value='"+field2+"' placeholder='"+field2+"'><br />"
		page+="</li>"
		page+="<li class='b'>"
		page+="<label for='field3'>Description</label><br />"
		page+="<input type='text' name='field3' id='field3' value='"+field3+"' placeholder='"+field3+"'><br />"
		page+="</li>"
		page+="<li class='b'>"
		page+="<label for='field4'>Message</label><br />"
		page+="<input type='text' name='field4' id='field4' value='"+field4+"' placeholder='"+field4+"'><br />"
		page+="</li>"
		page+="<li class='b'>"
		page+="<label for='field5'>BizUnit</label><br />"
		page+="<input list='bizunittype' name='field5' id='field5' value='"+bizunittypes[int(field5)]+"' placeholder='"+bizunittypes[int(field5)]+"'><br />"
		page+="</li>"
		page+="</ul class='b'>"
		page+="</li class='a'>"
		page+="<li class='a'>"
		page+="<ul class='b'>"
		page+="<li class='b'>"
		page+="<label for='field6'>Tech</label><br />"
		page+="<input type='text' name='field6' id='field6' value='"+field6+"' placeholder='"+field6+"'><br />"
		page+="</li>"
		page+="<li class='b'>"
		page+="<label for='field7'>Status</label><br />"
		page+="<input list='statustype' name='field7' id='field7' value='"+statustypes[int(field7)]+"' placeholder='"+statustypes[int(field7)]+"'><br />"
		page+="</li>"
		page+="<li class='b'>"
		page+="<label for='field8'>Event</label><br />"
		page+="<input type='text' name='field8' id='field8' value='"+field8+"' placeholder='"+field8+"'><br />"
		page+="</li>"
		page+="<li class='b'>"
		page+="<label for='field9'>Contact</label><br />"
		page+="<input type='text' name='field9' id='field9' value='"+field9+"' placeholder='"+field9+"'><br />"
		page+="</li>"
		page+="<li class='b'>"
		page+="<label for='field10'>Link</label><br />"
		page+="<input type='text' name='field10' id='field10' value='"+field10+"' placeholder='"+field10+"'><br />"
		page+="</li>"
		page+="<li class='b'>"
		page+="<label for='field11'>Notes</label><br />"
		page+="<input type='text' name='field11' id='field11' value='"+field11+"' placeholder='"+field11+"'><br />"
		page+="</li>"
		page+="</ul class='b'>"
		page+="</li class='a'>"
		page+="</ul class='a'>"
		# trust admin to enter correct data
		if (currentUser == 'ADMIN'):
			#print ("%s %s %s %s %s %s %s %s %s %s %s %s:" %(field0, field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11))
			page+="<br><input type='submit' value='save changes'/>"
		# but check everyone else
		else:
			page+="<br><input type='button' value='submit update request' onClick='checkChanges()'/>"
		page+="</form></p>"
		page+="<footer><hr><p><a href='/newSearch'>New Search</a></p><p><a href='/'>HOME</a></p><p>&copy; 2018.  All rights reserved.</p></footer>"
		page+="</div>"
		page+="</body></html>"
		return page

	# update DB with edited data record
	@cherrypy.expose
	def confirmData(self, field0, field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11):
		#print ("%s %s %s %s %s %s %s %s %s %s %s %s:" %(field0, field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11))
		currentUser = cherrypy.session['login']
		# DB query
		page="<!DOCTYPE html>"
		page+="<html> <head>"
		page+="<meta name='viewport' content='width=device-width'>"
		page+="<title>Demo Updates</title>"
		page+="<link rel='stylesheet' type='text/css' href='/css/style.css'></link>"
		page+="<script type='text/javascript' src='/js/test.js'></script>"
		page+="</head>"
		page+="<body>"
		page+="<div class='centerOutput'>"
		page+="<header><h2>Demo Updates</h2></header>"
		page +="<br>Updated Entry:"
		if (field5 in bizunittypes):
			bizunit = bizunittypes.index(field5)
		else:
			bizunit = '0'
		if (field7 in statustypes):
			status = statustypes.index(field7)
		else:
			status = '0'
		if (currentUser == 'ADMIN'):
			# update database
			#print ("objid: %s" %field0)
			db.cdgdevData.update( { "_id" : ObjectId(field0)}, { 'objid' : field0, 'date' : field1, 'title' : field2, 'description' : field3, 'message' : field4, 'bizunit' : bizunit, 'tech' : field6, 'status' : status, 'event' : field8, 'contact' : field9, 'link' : field10, 'notes' : field11 }, upsert=True, multi=False )
		page+="<ul class='a'>"
		# don't display objid associated with record
		#page+="<li class='a'>"
		#page+="<ul class='b'>"
		#page+="<li class='b'>"
		#page+="<p>ObjId: %s</p>" %field0
		#page+="</li>"
		#page+="</ul class='b'>"
		#page+="</li class='a'>"
		page+="<li class='a'>"
		page+="<ul class='b'>"
		page+="<li class='b'>"
		page+="<p>Date: %s</p>" %field1
		page+="</li>"
		page+="<li class='b'>"
		page+="<p>Title: %s</p>" %field2
		page+="</li>"
		page+="<li class='b'>"
		page+="<p>Description: %s</p>" %field3
		page+="</li>"
		page+="<li class='b'>"
		page+="<p>Message: %s</p>" %field4
		page+="</li>"
		page+="<li class='b'>"
		page+="<p>BizUnit: %s</p>" %field5
		page+="</li>"
		page+="</ul class='b'>"
		page+="</li class='a'>"
		page+="<li class='a'>"
		page+="<ul class='b'>"
		page+="<li class='b'>"
		page+="<p>Tech: %s</p>" %field6
		page+="</li>"
		page+="<li class='b'>"
		page+="<p>Status: %s</p>" %field7
		page+="</li>"
		page+="<li class='b'>"
		page+="<p>Event: %s</p>" %field8
		page+="</li>"
		page+="<li class='b'>"
		page+="<p>Contact: %s</p>" %field9
		page+="</li>"
		page+="<li class='b'>"
		page+="<p>Link: %s</p>" %field10
		page+="</li>"
		page+="<li class='b'>"
		page+="<p>Notes: %s</p>" %field11
		page+="</li>"
		page+="</ul class='b'>"
		page+="</li class='a'>"
		page+="</ul class='a'>"
		page+="<footer><hr><p><a href='/newSearch'>New Search</a></p><p><a href='/'>HOME</a></p><p>&copy; 2018.  All rights reserved.</p></footer>"
		page+="</div>"
		page+="</body></html>"
		return page

	# new search
	@cherrypy.expose
	def newSearch(self):
		if (cherrypy.session['login'] == "ADMIN"):
			return open(os.path.join(current_dir, u'adminQuery.html'))
		else:
			return open(os.path.join(current_dir, u'userQuery.html'))

	# site login
	@cherrypy.expose        
	def index(self):
		return open(os.path.join(current_dir, u'siteLogin.html'))

if __name__ == '__main__':
  
	# set up site-wide config
	# uncomment ssl lines for https
	cherrypy.config.update({'environment': 'production',
							'log.error_file': 'site.log',
							'log.screen': True,
							'tools.sessions.on': True,
							'tools.sessions.storage_type': 'file',
							'tools.sessions.storage_path': current_dir,
							'tools.sessions.timeout': 60,
							#'server.ssl_certificate': 'localhost.crt',
                          	#'server.ssl_private_key': 'localhost.key',
							'server.socket_host': '127.0.0.1',
							'server.socket_port': 8080})

	conf = {'/': {'tools.staticdir.root': current_dir},
			'/css': {'tools.staticdir.on': True,
					 'tools.staticdir.dir': os.path.join(current_dir, 'css')},
			'/pic': {'tools.staticdir.on': True,
					 'tools.staticdir.dir': os.path.join(current_dir, 'pic')},
			'/robots.txt': {'tools.staticfile.on': True,
							'tools.staticfile.filename': os.path.join(current_dir, 'robots.txt')},
			'/favicon.ico': {'tools.staticfile.on': True,
								'tools.staticfile.filename': os.path.join(current_dir, 'favicon.ico')},
			'/js': {'tools.staticdir.on': True,
					'tools.staticdir.dir': os.path.join(current_dir, 'js')}}

	cherrypy.quickstart(Root(), config=conf)

	  
