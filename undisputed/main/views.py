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

# twilio account information
account_sid = "AC4854286859444a07a57dfdc44c8eecea"
auth_token = "e0f79b613153fb5b2525f7552ef8cd1f"
twilio_number = "+19786730440"

# client used to send messages
client = TwilioRestClient(account_sid, auth_token)

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

join_league = "Solo: join league MyLeagueName MyLeaguePassword\n\n\Partnered: join league MyLeagueName MyLeaguePassword with PartnerUsername"

report = "Solo: beat OpponentUsername in MyLeagueName\n\n\
Partnered: beat Opponent1Username and Opponent2Username with PartnerUsername in MyLeagueName"

rankings = "rank MyLeagueName MyPartnerUsername"

stats = "Solo: stats MyLeagueName\n\n\
Partnered: stats MyLeagueName PartnerUsername"

@csrf_exempt
def incoming_text(request):
    print "incoming text...."

    number = request.GET.get('From')
    msg = request.GET.get('Body').lower().replace('\n', '')
    sections = msg.split(" ")
    print 'number: ' + number 
    print 'message: ' + msg

    # join undisputed username firstname lastname
    # TODO- all other valid characters, regex check on each section
    if re.match("^join undisputed [a-zA-Z0-9_]+ [a-zA-Z ]+$",msg):
        print "joining undisputed...."
        return handle_join_undisputed(number, sections)

    # options
    elif re.match("^options$",msg):
        return HttpResponse(createSmsResponse(options_query + options))

    # create solo|partner|partnered league name password
    # TODO: league name multiple words?
    elif re.match("^create (solo|partnered|partner) league [a-zA-Z0-9_]+ [a-zA-Z0-9_]+$", msg): 
        print "create league"
        return handle_create_league(number, sections)

    # join league_name password (with partner):
    elif re.match("^join [a-zA-Z0-9_]+ [a-zA-Z0-9_]+( with [a-zA-Z ]+)?$",msg):
        print "joining league....."
        return handle_join_league(number, sections)

    # beat opponent1 (and opponent2 with partner )in league_name
    elif re.match("^beat [a-zA-z0-9_]+ (and [a-zA-z0-9_]+ with [a-zA-z0-9_]+ )?in [a-zA-z0-9_]+$", msg):
        return handle_win(number, sections)

    elif re.match("^rank [a-zA-z0-9_]+$", msg):
        return handle_rank(number,sections)

    # stats league_name partner_username
    elif re.match("^stats [a-zA-z0-9_]+( [a-zA-z0-9_]+)?$", msg):
        print 'hit stats handler'
        sections = msg.split(" ")
        league_name = sections[1]

        return handle_stats(number,sections)

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

# sections[2] = username                                                                                                                                                                                 
# " ".join(sections[3:]) = name                                                                                                                                                                          
def handle_join_undisputed(number, sections):
    username = sections[2]
    name = " ".join(sections[3:])
    print 'username: ' + username
    print 'name: ' + name

    # checking if the account already exists                                                                                                                                                            
    try:
        player = Player.objects.get(phone_number=number)
        # account exists                                                                                                                                                                          
        return HttpResponse(createSmsResponse("You have already created an account with username %s" % player.username))
    except:
        # account does not exist                                                                                                                                                                    
        pass

    # trying to make an account                                                                                                                                                                          
    try:
        existing_player = Player.objects.get(username=username)
        # username taken                                                                                                                                                                            
        return HttpResponse(createSmsResponse("username %s already taken, please try another one" % username))
    except:
        # making account                                                                                                                               
        new_player = Player(name=name,username=username,phone_number=number)
        new_player.save()
        return HttpResponse(createSmsResponse("congrats, here are your options:\n" + options))

# sections[1] = type                                                                                                                                                                                     
# sections[3] = league name                                                                                                                                                                              
# sections[4] = league password                                                                                                                                                                          
def handle_create_league(number, sections):
    type = sections[1]
    name = sections[3]
    password = sections[4]
    print 'league type: %s' % type
    print 'league name: %s' % name
    print 'league password: %s' % password

    # checking if player exists                                                                                                                                                                          
    try:
        existing_player = Player.objects.get(phone_number=number)
        # player exists                                                                                                                                                                                  
    except:
        # player does not exist                                                                                                                                                                          
        return HttpResponse(createSmsResponse("Join Undisputed by texting: join undisputed MyUsername MyFirstName MyLastName"))

    # get team size                                                                                                                                                                                      
    if type == "solo":
        team_size = 1
    else:
        team_size = 2

    # check if league already exists                                                                                                                                                                     
    try:
        existing_league = League.objects.get(name=name)
        # league exists                                                                                                                                                                                  
        return HttpResponse(createSmsResponse("league already exists, please enter another name"))
    except:
        # league does not exist, create new one                                                                                                                                                          
        new_league = League(name=name,team_size=team_size,passcode=password)
        new_league.save()
        return HttpResponse(createSmsResponse("league all set up, tell your friends to join"))
        #TODO: return invalid league name, please try again

def handle_join_league(number, sections):
    try:
        existing_player = Player.objects.get(phone_number=number)
    except:
        return HttpResponse(createSmsResponse("you should register %s %s" % (team_size,password)))

    league_name = sections[1]
    passcode = sections[2]
    print "league name: %s" % league_name
    print 'passcode: %s' % passcode

    # check if league exists                                                                                                                                                                         
    try:
        existing_league = League.objects.get(name=league_name)
        # league exists                                                                                                                                                                              
    except:
        # league does not exist                                                                                                                                                                      
        return HttpResponse(createSmsResponse("This league does not exist. Please try again."))

    # check for right number of players on team                                                                                                                      
    if existing_league.team_size == 1 and len(sections) > 3:
        # trying to join a solo league with a partner                                                                                                                                                
        return HttpResponse(createSmsResponse("This is a solo league. You can't join with a partner."))
    elif existing_league.team_size == 2 and len(sections) < 5:
        # trying to join a partnered league without a partner                                                                                                                                        
        return HttpResponse(createSmsResponse("This is a team league. Join with a partner."))

    # check for a valid passcode                                                                                                                                                                     
    if existing_league.passcode != passcode:
        # invalid passcode                                                                                                                                                                           
        return HttpResponse(createSmsResponse("invalid password, please try again"))

    if existing_league.team_size == 2:
        partner_name = " ".join(sections[4:])
        print "partner %s" % partner_name

        # try to get the partner                                                                                                                                                                     
        try:
            # TODO: handle case where more than one player has the same name                                                                                                                         
            partner = Player.objects.get(name=partner_name)
            # partner exists                                                                                                                                                                         
        except:
            # partner does not exist                                                                                                                                                                 
            return HttpResponse(createSmsResponse("Invalid partner username"))

        # check if team is already in the league                                                                                                                                                     
        teams = Team.objects.filter(league=existing_league).all()
        for team in teams:
            if existing_player in team.members.all() and partner in team.members.all():
                # there already exists a team with existing_player and partner                                                                                                                       
                return HttpResponse(createSmsResponse("This team is already in this league"))

        # team does not exist yet. create it                                                                                                                                                         
        new_team = Team(league=existing_league,rating=2000)
        new_team.members.add(existing_player)
        new_team.members.add(partner)
        new_team.name = '%s and %s' % existing_player.name, partner.name
        new_team.save()

        return HttpResponse(createSmsResponse("league joined"))
    else:
        # TODO: implement joining solo leagues                                                                                                                                                       
        return HttpResponse(createSmsResponse('joining solo leagues not implemented yet.'))

def handle_stats(number, sections):
    # check if player is registered
    try:
        user = Player.objects.get(phone_number=number) 
        # player is registered
    except:
        # player is not registered
        return HttpResponse(createSmsResponse("You aren't on Undisputed. To join:\n join undisputed MyUsername MyFirstName MyLastName"))

    # check if league exists
    league_name = sections[1]
    try:
        existing_league = League.objects.get(name=league_name)
        # league exists
    except:
        # league does not exist
        return HttpResponse(createSmsResponse(league_name + " does not exist. Please try again."))

    teams = Team.objects.filter(league=existing_league).all()

    # check for the right team size
    if len(sections) == 2 and existing_league.team_size != 1:
        return HttpResponse(createSmsResponse('If you want stats for a partnered league: stats MyLeagueName PartnerUsername'))
    if len(sections) == 3 and existing_league.team_size != 2:
        return HttpResponse(createSmsResponse('If you want stats for a solo league: stats MyLeagueName'));

    # stats for partnered league
    if existing_league.team_size == 1:
        partner_username = sections[2]
        print 'partner username: %s' % partner_username

        # check if the partner exists
        try:
            partner = Player.objects.get(username=partner_username)
            # partner exists
        except:
            # partner does not exist
            return HttpResponse(createSmsResponse(partner_username + " does not exist. Please try again."))

        # find the user and partner's team object
        user_team = None
        for team in teams:
            if user in team.members.all() and partner in team.members.all():
                user_team = team
                break
                
        # the user's team does not exist
        if not user_team:
            return HttpResponse(createSmsResponse("You and " + partner_username + " are not a registered team in " + league_name + "."))

        # determine the suffix for the win streak
        if user_team.current_streak > 1 or not user_team.current_streak:
            streak_suffix = "wins"
        elif user_team.current_streak == 1:
            streak_suffix = "win"
        elif user_team.current_streak == -1:
            streak_suffix = "loss"
        else:
            streak_suffix = "losses"

        # build up the return string
        stats =  "Rank: %s\n" % user_team.ranking
        stats += "Rating: %s\n" % user_team.rating
        stats += "Wins: %s\n" % user_team.wins
        stats += "Losses: %s\n" % user_team.losses
        stats += "Current Streak: %s %s\n" % abs(user_team.current_streak), streak_suffix
        stats += "Longest Winning Streak: %s\n" % user_team.longest_winning_streak
        stats += "Longest Losing Streak: %s" % user_team.longest_loss_streak

        return HttpResponse(createSmsResponse(stats))
    
    # stats for an individual league
    # TODO: implement this
    else:
        return HttpResponse(createSmsResponse('Sorry, this has not been implemented yet.'))

# sections[1] = league name
# sections[2] = partner username
def handle_rank(number, sections):
    print "ranking..."
    league_name = sections[1]
    print 'league: %s' % league_name

    # check if the user is registered                        
    try:
        user = Player.objects.get(phone_number=number)
        # user is registered
    except:
        # user is not registered
        return HttpResponse(createSmsResponse("Join Undisputed by texting: join undisputed MyUsername MyFirstName MyLastName"))

    # check if the league exists
    try:
        existing_league = League.objects.get(name=league_name)
        # league exists
    except:
        # league does not exist
        return HttpResponse(createSmsResponse(league_name + " does not exist. Please try again."))

    teams = Team.objects.filter(league=existing_league).order_by("rating").all().reverse()

    # get rankings for a partnered league
    if existing_league.team_size == 2:
        # check that a partner was specified
        if len(sections) < 3:
            return HttpResponse(createSmsResponse('%s is a partnered league and you didn\'t specify a partner. Try: rank MyLeagueName MyPartnerName' % league_name))

        partner_username = sections[2]
        print 'partner username: %s' partner_username

        # check if the partner exists
        try:
            partner = Player.objects.get(username=partner_username)
            # partner exists
        except:
            # partner does not exist
            return HttpResponse(createSmsResponse(partner_username + " does not exist. Please try again."))

        present = False
        for team in teams:
            if user in team.members.all() and partner in team.members.all():
                present = True
                break

        if not present:
            return HttpResponse(createSmsResponse("You and %s are not registered in %s. Please try again." % partner_username, league_name))

    # get rankings for a solo league
    # TODO: implement this
    else:
        return HttpReponse(createSmsResponse('Not implemented yet. Sorry'))

    # build up a string of rankings to return
    rankings = ""
    count = 0
    # return rankings for at most 10 teams, while making sure that we don't exceed the twilio character limit
    for count in range(min(10, len(teams))):
        # TODO: add some defense against people with really long names
        # build up the next ranking entry
        next_entry = '%s. %s (%s)\n' % count + 1, teams[count].name, teams[count].rating
        
        # if it fits, add it to the response string
        if len(next_entry) + len(rankings) < 160:
            rankings += next_entry
        else:
            break

    return HttpResponse(createSmsResponse(rankings))

# beat opponent1 (and opponent2 with partner )in league_name
# sections[1] = loser1
# sections[-1] = league name
# if partnered:
#    sections[3] = loser2
#    sections[5] = partner
def handle_win(number, sections):
    # check if the user is registered
    try:
        winner = Player.objects.get(phone_number=number)
        # user is registered
        print "winner: %s" % winner.username
    except:
        # user is not registered
        return HttpResponse(createSmsResponse("Join Undisputed by texting: join undisputed MyUsername MyFirstName MyLastName"))

    # check if the league exists
    league_name = sections[-1]
    print 'league name: %s' % league_name
    try:
        existing_league = League.objects.get(name=league_name)
        # the league exists
    except:
        # the league does not exist
        return HttpResponse(createSmsResponse(league_name + " does not exist. Please try again."))

    # check if loser1 exists
    loser1_username = sections[1]
    print 'loser1: %s' % loser1_username
    try:
        loser1 = Player.objects.get(username=loser1_username)
        # loser1 exists
    except:
        # loser1 does not exist
        return HttpResponse(createSmsResponse(loser_username + " does not exist. Please try again."))

    teams = Team.objects.filter(league=existing_league).all()
    
    # handle win for partnered league
    if existing_league.team_size == 2:
        
        # check that message was indeed for a partnered league
        if len(sections) != 8:
            return HttpResponse(createSmsResponse('If you want to report a win for a partnered league: beat opponent1 and opponent2 with partner in league_name'))

        # check if partner exists
        partner_username= sections[5]
        print 'partner: %s' % partner_username
        try:
            partner = Player.objects.get(username=partner_username)
            # partner exists
        except:
            # partner does not exist
            return HttpResponse(createSmsResponse(partner_username + " does not exist. Please try again."))

        # check if loser2 exists
        loser2_username = sections[3]
        print 'loser2: %s' % loser2_username
        try:
            loser2 = Player.objects.get(username=loser2_username)           
            # loser2 exists
        except:
            # loser2 does not exist
            return HttpResponse(createSmsResponse(loser2_username + " does not exist. Please try again."))

        # search for a team between winner and partner
        winning_team = None
        for team in teams:
            if winner in team.members.all() and partner in team.members.all():
                winning_team = team
                break

        if not winning_team:
            # no team between winner and partner
            return HttpResponse(createSmsResponse("You and " + partner_username + " are not in a registered team in " + league_name + "."))

        # search for a team between loser1 and loser2
        losing_team = None
        for team in teams:
            if loser1 in team.members.all() and loser2 in team.members.all():
                losing_team = team
                break

        if not losing_team:
            # no team between loser1 and loser2
            return HttpResponse(createSmsResponse(loser1_username + " and " + loser2_username + " are not a registered team in " + league_name + "."))

    else: # handle win for solo league
        # check that message was indeed for a solo league
        if len(sections) != 5:
            return HttpResponse(createSmsResponse('If you want to report a win for a solo league: beat opponent in league_name'))

        # search for winner's team
        winning_team = None
        for team in teams:
            if winner in team.members.all():
                winning_team = team
                break

        if not winning_team:
            # winner is not in the league
            return HttpResponse(createSmsResponse("You are not in " + league_name + "."))

        # search for the loser's team
        losing_team = None
        for team in teams:
            if loser in team.members.all():
                losing_team = team
                break

        if not losing_team:
            # loser is not in the league
            return HttpResponse(createSmsResponse(loser_username + " is not in " + league_name + "."))

    # save the result
    new_result = Result(league=existing_league, winner=winning_team, loser=losing_team, time=datetime.now())
    new_result.save()

    # use Elo's algorithm to calculate the new ratings
    old_winner_rating = winning_team.rating
    old_loser_rating = losing_team.rating

    spread = 1000.0
    volatility = 80.0

    q_winner = 10**(old_winner_rating/spread)
    q_loser = 10**(old_loser_rating/spread)
    expected_winner = q_winner / (q_winner + q_loser)
    expected_loser = q_loser / (q_winner + q_loser)

    new_winner_rating = old_winner_rating + volatility * (1 - expected_winner)
    new_loser_rating = old_loser_rating + volatility * (0 - expected_loser)

    winning_team.rating = new_winner_rating
    losing_team.rating = new_loser_rating

    # update win-loss counts
    winning_team.wins += 1
    losing_team.losses += 1

    # update streak records for the winning team
    if winning_team.current_streak > 0:
        winning_team.current_streak += 1
    else:
        winning_team.current_streak = 1

    winning_team.longest_win_streak = max(winning_team.longest_win_streak,winning_team.current_streak)

    # update streak records for the losing team
    if losing_team.current_streak < 0:
        losing_team.current_streak -= 1
    else:
        losing_team.current_streak = -1

    losing_team.longest_loss_streak = min(losing_team.longest_loss_streak,losing_team.current_streak)

    # save the new stats
    winning_team.save()
    losing_team.save()

    # use the new ratings to calculate new rankings
    teams = Team.objects.filter(league=existing_league).order_by("rating").all().reverse()

    rank = 1
    for team in teams:
        team.ranking = rank
        team.save()
        rank += 1

    # TODO: get teams using team name always?
    winning_team = Team.objects.get(league=existing_league, name=winning_team.name)
    losing_team = Team.objects.get(league=existing_league, name=losing_team.name)

    # in the case of a solo league, send confirmation messages to both parties
    if existing_league.team_size == 1:
        client.sms.messages.create(
            to=str(loser.phone_number),
            from_=twilio_number,
            body="You were defeated by %s in %s. Your new rating is %s and you are ranked %s" % (winner.username, existing_league.name, int(losing_team.rating), losing_team.ranking))

        return HttpResponse(
            createSmsResponse(
                "Congrats! Your new rating is %s and your are ranked %s in %s. A notification was sent to %s." % int(winning_team.rating), winning_team.ranking, winning_team.league, loser.username))

    # in the case of a partnered league, send confirmation to all four parties
    else:
        client.sms.messages.create(
            to=str(loser1.phone_number),
            from_=twilio_number,
            body="You and %s were defeated by %s and %s in %s. Your new rating is %s and you are ranked %s." % (loser2.username, winner.username, partner.username, league_name, int(losing_team.rating), losing_team.ranking))

        client.sms.messages.create(
            to=str(loser2.phone_number),
            from_=twilio_number,
            body="You and %s were defeated by %s and %s in %s. Your new rating is %s and you are ranked %s." % (loser1.username, winner.username, partner.username, league_name, int(losing_team.rating), losing_team.ranking))

        client.sms.messages.create(
            to=str(partner.phone_number),
            from_=twilio_number,
            body="You and %s defeated %s and %s in %s. Your new rating is %s and you are ranked %s." % (winner.username, loser1.username, loser2.username, league_name, int(winning_team.rating), winning_team.ranking))
   
        return HttpResponse(
            createSmsResponse(
                "Congrats! Notifications were sent to %s, %s, and %s. Your new rating is %s and you are ranked %s." % (partner.username, loser1.username, loser2.username, int(winning_team.rating), winning_team.ranking)))

