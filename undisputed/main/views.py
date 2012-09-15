# Create your views here.
import twilio.twiml

from django.template import Context, loader
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django import forms
from django.template import RequestContext

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login, logout
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.core.exceptions import ValidationError

from django.core.files.base import ContentFile
from django.core.mail import send_mail
import base64
import hmac, sha
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.contrib import auth
from django.core.mail import send_mail
from django.core.mail import EmailMessage

from subprocess import *
from datetime import *
from xml.dom.minidom import getDOMImplementation,parse,parseString
from main.models import Player, League, Team, Result
from random import choice
import re
import os
import cgi
import hashlib
import urllib2
import json
import base64
import hmac
import settings

@csrf_exempt
def incoming_text(request):
	options = "Your options are:\n\
		Join Undisputed: join undisputed MyUsername MyFirstName MyLastName\n\
	Create Solo League: create solo league MyLeagueName MyLeaguePassword\n\
  Create Partnered League: create partnered league MyLeagueName MyLeaguePassword\n\
  Join Solo League: join solo league MyLeagueName MyLeaguePassword\n\
  Join Partnered League: join partnered league MyLeagueName PartnerUsername MyLeaguePassword\n\
  Report Individual Win: win MyLeagueName OpponentUsername\n\
  Report Partnered Win: win MyLeagueName PartnerUsername Opponent1Username Opponent2Username\n\
 View Rankings: rank MyLeagueName\n\
  View Personal Stats: stats MyLeagueName\n"
	print "incoming...."
	number = request.GET.get('From')
	msg = request.GET.get('Body')
	sections = msg.split(" ")
	if re.match("^join undisputed [a-zA-Z0-9_]+ [a-zA-Z ]+$",msg): #TODO- all other valid characters, regex check on each section
  		print "joining undisputed...."
  		username = sections[2]
		name = "".join(sections[3:])
  		try:
  			existing_player = Player.objects.get(username=username)
  			return HttpResponse(createSmsResponse("username %s already taken, please try another one" % username))
		except:
			new_player = Player(name=name,username=username,phone_number=number)
			new_player.save()
  			return HttpResponse(createSmsResponse("congrats, here are your options: (...all the options...)"))

  	#create league [name] [team size] [password]
  	elif re.match("^options$",msg):
  		return HttpResponse(createSmsResponse(options))
	elif re.match("^create (solo|partnered|partner) league [a-zA-Z0-9_]+ [a-zA-Z0-9_]+$",msg):  #Todo: league name multiple words?
		print "create league"
		try:
			existing_player = Player.objects.get(phone_number=number)
		except:
			return HttpResponse(createSmsResponse("you should register %s %s" % (team_size,password)))	
		name = sections[3]
		if sections[1] == "solo":
			team_size = 1
		else:
			team_size = 2
		password = sections[4]
		print password
		try: 
			#see if league name already exists
			existing_league = League.objects.get(name=name)
			return HttpResponse(createSmsResponse("league already exists, please enter another name"))
		except:
			print "create new league"
			#create new league
			new_league = League(name=name,team_size=team_size,passcode=password)
			new_league.save()
			print "new league saved"
			return HttpResponse(createSmsResponse("league all set up, tell your friends to join"))
		#TODO: return invalid league name, please try again
	#elif team 		join league (league name, password):
	#join league as individual
	elif re.match("^join [a-zA-Z0-9_]+ [a-zA-Z0-9_]+( with [a-zA-Z0-9_]+)?$",msg):
		print "joining league....."
		try:
			existing_player = Player.objects.get(phone_number=number)
		except:
			return HttpResponse(createSmsResponse("you should register %s %s" % (team_size,password)))
		league_name = sections[1]
		print "league name: %s" % league_name
		try:
			existing_league = League.objects.get(name=league_name)
			#check for right number of players on team
			if existing_league.team_size == 1 and len(sections) > 3:
				return HttpResponse(createSmsResponse("This is only an individual league"))
			elif existing_league.team_size == 2 and len(sections) == 3:
				return HttpResponse(createSmsResponse("This is a team league: add your partner too"))
		except:
			return HttpResponse(createSmsResponse("invalid team name, please try again"))
		passcode = sections[2]
		print "passcode: %s" % passcode
		if existing_league.passcode == passcode:
			if len(sections) >3:
				partner_name = sections[-1]
				print "partner %s" % partner_name
				try:
					partner = Player.objects.get(name=partner_name)
				except:
					return HttpResponse(createSmsResponse("Invalid partner username"))
			new_team = Team(league=existing_league,rating=0)
			new_team.save()
			new_team.members.add(existing_player)
			if partner:
				new_team.members.add(partner)
			new_team.name = existing_player.name
			new_team.save()
			return HttpResponse(createSmsResponse("league joined"))
		else:
			return HttpResponse(createSmsResponse("invalid password, please try again"))  
	else:
		return HttpResponse(createSmsResponse("Text 'help' to view your options."))
	



def createSmsResponse(responsestring):
	impl = getDOMImplementation()
	responsedoc = impl.createDocument(None,"Response",None)
	top_element = responsedoc.documentElement
	sms_element = responsedoc.createElement("Sms")
	top_element.appendChild(sms_element)
	text_node = responsedoc.createTextNode(responsestring)
	sms_element.appendChild(text_node)
	html = responsedoc.toxml(encoding="utf-8")
	return html