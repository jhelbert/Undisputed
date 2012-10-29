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
    
    print "incoming...."
    number = request.GET.get('From')
    msg = request.GET.get('Body').lower().replace('\n', '')
    sections = msg.split(" ")
    print 'message: ' + msg
    if re.match("^join undisputed [a-zA-Z0-9_]+ [a-zA-Z ]+$",msg): #TODO- all other valid characters, regex check on each section
        print "joining undisputed...."
        username = sections[2]
        print 'username: ' + username
        name = "".join(sections[3:])
        print 'name: ' + name
        try: 
            player = Player.objects.get(phone_number=number)
            return HttpResponse(createSmsResponse("You have already created an account with username %s" % player.username))
        except:
            pass
        print 'trying to make an account'
        try:
            print 'username taken'
            existing_player = Player.objects.get(username=username)
            return HttpResponse(createSmsResponse("username %s already taken, please try another one" % username))
        except:
            print 'making account'
            new_player = Player(name=name,username=username,phone_number=number)
            print 'made player object'
            new_player.save()
            print 'saved player object to db'
            return HttpResponse(createSmsResponse("congrats, here are your options:\n" + options))

    #create league [name] [team size] [password]
    elif re.match("^options$",msg):
        return HttpResponse(createSmsResponse(options_query + options))
    elif re.match("^create (solo|partnered|partner) league [a-zA-Z0-9_]+ [a-zA-Z0-9_]+$", msg):  #Todo: league name multiple words?
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
    elif re.match("^join( league)? [a-zA-Z0-9_]+ [a-zA-Z0-9_]+(( with)? [a-zA-Z0-9_]+)?$",msg):
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
                partner_name = " ".join(sections[3:])
                print "partner %s" % partner_name
                #TODO: look up by username if collision
                try:
                    partner = Player.objects.get(name=partner_name)
                except:
                    return HttpResponse(createSmsResponse("Invalid partner username"))
            print "AA"
            teams = Team.objects.filter(league=existing_league).all()
            print "BB"
            if len(teams) > 0:
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
            print "CC"

            print "DD"
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
    elif re.match("^beat [a-zA-z0-9_]+ (and [a-zA-z0-9_]+ with [a-zA-z0-9_]+ )?in [a-zA-z0-9_]+$", msg):
        sections = msg.split(" ")
        league_name = sections[-1]
        loser1_username = sections[1]

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
            loser1 = Player.objects.get(username=loser1_username)
        except:
            return HttpResponse(createSmsResponse(loser_username + " does not exist. Please try again."))

        teams = Team.objects.filter(league=existing_league).all()
        
        if len(sections) == 8:
            loser2_username = sections[3]
            partner_username= sections[5]

            try:
                partner = Player.objects.get(username=partner_username)           
            except:
                return HttpResponse(createSmsResponse(partner_username + " does not exist. Please try again."))

            try:
                loser2 = Player.objects.get(username=loser2_username)           
            except:
                return HttpResponse(createSmsResponse(loser2_username + " does not exist. Please try again."))

            if existing_league.team_size != 2:
                return HttpResponse(createSmsResponse(league_name + " is a partnered league, and you reported a solo win."))

            winning_team = None
            for team in teams:
                if winner in team.members.all() and partner in team.members.all():
                    winning_team = team
                    break

            if winning_team == None:
                return HttpResponse(createSmsResponse("You and " + partner_username + " are not in a registered team in " + league_name + ". Please try again"))
    
            losing_team = None
            for team in teams:
                if loser1 in team.members.all() and loser2 in team.members.all():
                    losing_team = team
                    break

            if losing_team == None:
                return HttpResponse(createSmsResponse(loser1_username + " and " + loser2_username + " are not a registered team in " + league_name + "."))

        else:
            if existing_league.team_size != 1:
                return HttpResponse(createSmsResponse(league_name + " is a solo league, and you reported a partnered win."))

            winning_team = None
            for team in teams:
                print "team %s" % team
                if winner in team.members.all():
                    winning_team = team
                    print "winning_team: %s" % winning_team
                    break

            if winning_team == None:
                return HttpResponse(createSmsResponse("You are not in " + league_name + ". Please try again"))

            losing_team = None
            for team in teams:
                if loser in team.members.all():
                    losing_team = team
                    print "losing_team: %s" % losing_team
                    break

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

        winning_team.wins += 1
        losing_team.losses += 1
        if winning_team.current_streak > 0:
            winning_team.current_streak += 1
        else:
            winning_team.current_streak = 1
        winning_team.longest_win_streak = max(winning_team.longest_win_streak,winning_team.current_streak)
        if losing_team.current_streak < 0:
            losing_team.current_streak -= 1
        else:
            losing_team.current_streak = -1
        losing_team.longest_loss_streak = min(losing_team.longest_loss_streak,losing_team.current_streak)
        winning_team.save()
        losing_team.save()

        teams = Team.objects.filter(league=existing_league).order_by("rating").all().reverse()

        rank = 1
        for team in teams:
            team.ranking = rank
            team.save()
            rank += 1

        winning_team = Team.objects.get(league=existing_league, name=winning_team.name)
        losing_team = Team.objects.get(league=existing_league, name=losing_team.name)

        account_sid = "AC4854286859444a07a57dfdc44c8eecea"
        auth_token = "e0f79b613153fb5b2525f7552ef8cd1f"
        client = TwilioRestClient(account_sid, auth_token)
     
        if existing_league.team_size == 1:
            client.sms.messages.create(to=str(loser.phone_number), from_="+19786730440", body="You were defeated by %s in %s. Your new rating is %s and you are ranked %s" % (winner.username, existing_league.name, int(losing_team.rating), losing_team.ranking))

            return HttpResponse(createSmsResponse("Congratulations! Your new rating is %s and your are ranked %s in %s. A notification was sent to %s." % (int(winning_team.rating),winning_team.ranking,winning_team.league,loser.username)))
        else:
            client.sms.messages.create(to=str(loser1.phone_number), from_="+19786730440", body="You and %s were defeated by %s and %s in %s. Your new rating is %s and you are ranked %s." % (loser2.username, winner.username, partner.username, league_name, int(losing_team.rating), losing_team.ranking))
            client.sms.messages.create(to=str(loser2.phone_number), from_="+19786730440", body="You and %s were defeated by %s and %s in %s. Your new rating is %s and you are ranked %s." % (loser1.username, winner.username, partner.username, league_name, int(losing_team.rating), losing_team.ranking))
            client.sms.messages.create(to=str(partner.phone_number), from_="+19786730440", body="You and %s defeated %s and %s in %s. Your new rating is %s and you are ranked %s." % (winner.username, loser1.username, loser2.username, league_name, int(winning_team.rating), winning_team.ranking))
       
            return HttpResponse(createSmsResponse("Congratulations! Notifications were sent to %s, %s, and %s. Your new rating is %s and you are ranked %s." % (partner.username, loser1.username, loser2.username, int(winning_team.rating), winning_team.ranking)))

    elif re.match("^rank [a-zA-z0-9_]+$", msg):
        print "ranking..."
        league_name = msg.split(" ")[1]
        print "AA"
        try:
            user = Player.objects.get(phone_number=number) 
        except:
            return HttpResponse(createSmsResponse("Join Undisputed by texting: join undisputed MyUsername MyFirstName MyLastName"))
        print "B"
        try:
            existing_league = League.objects.get(name=league_name)
        except:
            return HttpResponse(createSmsResponse(league_name + " does not exist. Please try again."))
        print "C"
        teams = Team.objects.filter(league=existing_league).order_by("rating").all().reverse()
        print "C2"
        present = False
        for team in teams:
            if user in team.members.all():
                present = True
                break
        print "D"
        if not present:
            return HttpResponse(createSmsResponse("You are not registered in " + league_name + ". Please try again"))

        rankings = ""
        count = 0
        while len(rankings) < 160 and count < min(10, len(teams)):
            print rankings
            rankings += str(count + 1) + ". " + " & ".join([member.username for member in teams[count].members.all()]) + " (" + str(teams[count].rating) + ")\n"
            count += 1
        print "E"
        return HttpResponse(createSmsResponse(rankings))
    elif re.match("^stats [a-zA-z0-9_]+( [a-zA-z0-9_]+)?$", msg):
        print 'hit stats handler'
        sections = msg.split(" ")
        league_name = sections[1]

        try:
            user = Player.objects.get(phone_number=number) 
        except:
            return HttpResponse(createSmsResponse("You aren't on Undisputed. To join:\n join undisputed MyUsername MyFirstName MyLastName"))

        try:
            existing_league = League.objects.get(name=league_name)
        except:
            return HttpResponse(createSmsResponse(league_name + " does not exist. Please try again."))

        teams = Team.objects.filter(league=existing_league).all()
        
        if len(sections) == 2:
            if existing_league.team_size != 1:
                return HttpResponse(createSmsResponse(league_name + " is a partnered league, and you asked for stats about a solo league."))

            user_team = None
            for team in teams:
                if user in team.members.all():
                    user_team = team
                    break
                
                if user_team == None:
                    return HttpResponse(createSmsResponse("You are not a part of " + league_name + "."))
        else:
            partner_username = sections[2]

            try:
                partner = Player.objects.get(username=partner_username)           
            except:
                return HttpResponse(createSmsResponse(partner_username + " does not exist. Please try again."))

            if existing_league.team_size != 2:
                return HttpResponse(createSmsResponse(league_name + " is a solo league, and you asked for stats about a partnered league."))

            user_team = None
            for team in teams:
                if user in team.members.all() and partner in team.members.all():
                    user_team = team
                    break

            if user_team == None:
                return HttpResponse(createSmsResponse("You and " + partner_username + " are not a registered team in " + league_name + "."))

        if user_team.current_streak > 1 or user_team.current_streak == 0:
            streak_suffix = "wins"
        elif user_team.current_streak == 1:
            streak_suffix = "win"
        elif user_team.current_streak == -1:
            streak_suffix = "loss"
        else:
            streak_suffix = "losses"

        stats = "Rank: " + str(user_team.ranking) + "\n\
            Rating: " + str(user_team.rating) + "\n\
            Wins: " + str(user_team.wins) + "\n\
            Losses: " + str(user_team.losses) + "\n\
            Current Streak: " + str(abs(user_team.current_streak)) + " " + streak_suffix + "\n\
            Longest Winning Streak: " + str(user_team.longest_win_streak) + "\n\
            Longest Losing Streak: " + str(user_team.longest_loss_streak)

        return HttpResponse(createSmsResponse(stats))
    elif re.match("^(?i)a$", msg):
        print 'hit join undisputed'
        return HttpResponse(createSmsResponse(join))

    elif re.match("^(?i)b$", msg):
        return HttpResponse(createSmsResponse(create))

    elif re.match("^(?i)c$", msg):
        return HttpResponse(createSmsResponse(join_league))

    elif re.match("^(?i)d$", msg):
        return HttpResponse(createSmsResponse(report))

    elif re.match("^(?i)e$", msg):
        return HttpResponse(createSmsResponse('rank MyLeagueName'))

    elif re.match("^(?i)f$", msg):
        return HttpResponse(createSmsResponse("Solo: stats MyLeagueName\n\nPartnered: stats MyLeagueName PartnerUsername"))
    else:
        return HttpResponse(createSmsResponse("Text 'options' to view your options."))

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


options_query = "What would you like to do?:\n"
options =  "(a) Join Undisputed\n"
options += "(b) Create League\n"
options += "(c) Join League\n"
options += "(d) Report Win\n"
options += "(e) View Rankings\n"
options += "(f) View Personal Stats\n"

join = "join undisputed MyUsername MyFirstName MyLastName"

create = "Solo: create solo league MyLeagueName MyLeaguePassword\n\n\
         Partnered: create partnered league MyLeagueName MyLeaguePassword"

join_league = "Solo: join league MyLeagueName MyLeaguePassword\n\n\
              Partnered: join league MyLeagueName MyLeaguePassword with PartnerUsername"

report = "Solo: beat OpponentUsername in MyLeagueName\n\n\
         Partnered: beat Opponent1Username and Opponent2Username with PartnerUsername in MyLeagueName"

rankings = "rank MyLeagueName"

stats = "Solo: stats MyLeagueName\n\n\
        Partnered: stats MyLeagueName PartnerUsername"

