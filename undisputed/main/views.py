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

from twilio.rest import TwilioRestClient

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
            player = Player.objects.get(phone_number=number)
            return HttpResponse(createSmsResponse("You have already created an account with username %s" % player.username))
        except:
            pass
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
    


    #elif team  join league (league name, password):
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
            print "AA"
            teams = Team.objects.filter(league=existing_league).all()
            print "BB"
            for team in teams:
                print "team %s" % team
                if existing_player in team.members.all():
                    print "player exists"
                    try:
                        print "partner exists"
                        if partner in team.members.all():
                            return HttpResponse(createSmsResponse("This team is already in this league"))
                    except:
                        print "no partner exists"
                        return HttpResponse(createSmsResponse("You are already in this league"))
            winning_team = team

            new_team = Team(league=existing_league,rating=2000)
            new_team.save()
            new_team.members.add(existing_player)
            new_team.name = existing_player.name
            if partner:
                new_team.members.add(partner)
                new_team.name = existing_player.name + " and " +  partner.name
            new_team.save()

            return HttpResponse(createSmsResponse("league joined"))
        else:
            return HttpResponse(createSmsResponse("invalid password, please try again"))  

    elif re.match("^beat [a-zA-z0-9_]+ in [a-zA-z0-9_]+$", msg):
        sections = msg.split(" ")
        league_name = sections[-1]
        loser_username = sections[1]
        
        try:
            winner = Player.objects.get(phone_number=number) 
            print "winner: %s" % winner
        except:
            return HttpResponse(createSmsResponse("Join Undisputed by texting: join undisputed MyUsername MyFirstName MyLastName"))

        try:
            existing_league = League.objects.get(name=league_name)
        except:
            return HttpResponse(createSmsResponse(league_name + " does not exist. Please try again."))

        try:
            loser = Player.objects.get(username=loser_username)           
        except:
            return HttpResponse(createSmsResponse(loser_username + " does not exist. Please try again."))
        print "continue -2"
        teams = Team.objects.filter(league=existing_league).all()
        print "continue -1"
        winning_team = None
        for team in teams:
            print "team %s" % team
            if winner in team.members.all():
                winning_team = team
                print "winning_team: %s" % winning_team
                break
        print "continue 0"
        if winning_team == None:
            return HttpResponse(createSmsResponse("You are not in " + league_name + ". Please try again"))
        print "continue 1"
        losing_team = None
        for team in teams:
            if loser in team.members.all():
                losing_team = team
                print "losing_team: %s" % losing_team
                break
        print "continue 2"
        if losing_team == None:
            return HttpResponse(createSmsResponse(loser_username + " is not in " + league_name + "."))

        new_result = Result(league=existing_league, winner=winning_team, loser=losing_team, time=datetime.now())
        new_result.save()
        print "continue 3"
        old_winner_rating = winning_team.rating
        old_loser_rating = losing_team.rating
        print "continue 4"
        spread = 1000.0
        volatility = 80.0
        print "continue 5"
        q_winner = 10**(old_winner_rating/spread)
        q_loser = 10**(old_loser_rating/spread)
        expected_winner = q_winner / (q_winner + q_loser)
        expected_loser = q_loser / (q_winner + q_loser)
        print "continue 6"
        new_winner_rating = old_winner_rating + volatility * (1 - expected_winner)
        new_loser_rating = old_loser_rating + volatility * (0 - expected_loser)
        print "continue 7"
        winning_team.rating = new_winner_rating
        losing_team.rating = new_loser_rating
        print "winning_team.rating %s" % winning_team.rating
        print "losing_team.rating %s" % losing_team.rating
        winning_team.save()
        losing_team.save()

        account_sid = "AC4854286859444a07a57dfdc44c8eecea"
        auth_token = "e0f79b613153fb5b2525f7552ef8cd1f"
        client = TwilioRestClient(account_sid, auth_token)
     
        message = client.sms.messages.create(to=str(loser.phone_number), from_="+19786730440", body="You were defeated by " + winner.username + " in " + league_name)

        return HttpResponse(createSmsResponse("Congratulations! Your new rating is A notification was sent to " + loser.username + "."))
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