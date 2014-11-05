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
from main.models import Player, Team, Result, Competition, League
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
options += "(b) Report Win\n"
options += "(c) View Rankings\n"
options += "(d) View Personal Stats\n"

join = "join undisputed username:MyUsername name:MyFirstName MyLastName"

report = "beat OpponentUsername in CompetitionName"

rankings = "CompetitionName rankings"

stats = "my CompetitionName stats"

@csrf_exempt
def incoming_text(request):
    print "incoming text...."

    number = request.GET.get('From')
    msg = request.GET.get('Body').lower().replace('\n', '')
    sections = msg.split(" ")
    print 'number: ' + number 
    print 'message: ' + msg

    try:
        player = Player.objects.get(phone_number=number)

        # ###
        # if not player.name:
        #     player.name = msg
        #     player.save()
        #     return HttpResponse(createSmsResponse("Hi, %s! Enter a username" % (player.name)))
        
        if not player.username:  
            player.username = msg
            player.save()
            return HttpResponse(createSmsResponse("You're all set up!\n" + options_query + options))

    except:
        print "creating new player"
        player = Player(phone_number=number)
        player.save()
        print "created"
        return HttpResponse(createSmsResponse("Welcome to Undisputed. Enter your initials."))

    # join undisputed username firstname lastname
    # TODO- all other valid characters, regex check on each section


    if re.match("^me$",msg):
        return handle_me(number)
    # options
    elif re.match("^options$",msg):
        return HttpResponse(createSmsResponse(options_query + options))

    # beat opponent1 (and opponent2 with partner )in competition_name
    elif re.match("^beat [a-zA-z0-9_]+ (and [a-zA-z0-9_]+ with [a-zA-z0-9_]+ )?in [a-zA-z0-9_]+$", msg):
        return handle_win(number, sections)

    # competition_name rankings
    elif re.match("^[a-zA-z0-9_]+ rankings$", msg):
        return handle_rank(number,sections)

    # my competition_name stats
    elif re.match("^my [a-zA-z0-9_]+( [a-zA-z0-9_]+)? stats$", msg):
        print 'hit stats handler'
        sections = msg.split(" ")

        return handle_stats(number,sections)

    elif re.match("^(?i)a$", msg):
        return HttpResponse(createSmsResponse(join))

    elif re.match("^(?i)b$", msg):
        return HttpResponse(createSmsResponse(report))

    elif re.match("^(?i)c$", msg):
        return HttpResponse(createSmsResponse('CompetitonName rankings'))

    elif re.match("^(?i)d$", msg):
        return HttpResponse(createSmsResponse("my CompetitionName stats"))

     # create solo|partner|partnered league name password
    # TODO: league name multiple words?
    elif re.match("^create (solo|partnered|partner) league [a-zA-Z0-9_]+ [a-zA-Z0-9_]+$", msg): 
        print "create league"
        return handle_create_league(number, sections)

    # join league_name password (with partner):
    elif re.match("^join [a-zA-Z0-9_]+ [a-zA-Z0-9_]+( with [a-zA-Z ]+)?$",msg):
        print "joining league....."
        return handle_join_league(number, sections)


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


def handle_me(number):
    player = Player.objects.get(phone_number=number)
    text = "Name:%s\n" % player.name
    text += "username:%s\n" % player.username
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
        return HttpResponse(createSmsResponse("Welcome, here are your options:\n" + options))

def handle_stats(number, sections):
    # check if player is registered
    try:
        user = Player.objects.get(phone_number=number) 
        # player is registered
    except:
        # player is not registered
        return HttpResponse(createSmsResponse("You aren't on Undisputed. To join:\n join undisputed MyUsername MyFirstName MyLastName"))

    # check if competition exists
    competition_name = sections[1]
    print "competition_name:%s" % competition_name
    try:
        competition = Competition.objects.get(name=competition_name)
        # competition exists
    except:
        # competition does not exist
        return HttpResponse(createSmsResponse(competition_name + " does not exist. Please try again."))
    print "got competition"
    teams = Team.objects.filter(league=league).all()
    print teams
    user_team = None
    for team in teams:
        if user.username ==  team.members.username:
            user_team = team
            break
    print "got teams"    
    # the user's team does not exist
    if not user_team:
        return HttpResponse(createSmsResponse("You are not a registered team in " + competition_name + "."))
    print 'registed team'
    # determine the suffix for the win streak

    if user_team.current_streak > 1 or not user_team.current_streak:
        streak_suffix = "wins"
        print "wins suffix"
    elif user_team.current_streak == 1:
        streak_suffix = "win"
    elif user_team.current_streak == -1:
        streak_suffix = "loss"
    else:
        streak_suffix = "losses"
    print "got streak suffix"
    # build up the return string
    stats =  "Rank: %s / %s\n" % (user_team.ranking, len(teams))
    stats += "Rating: %s\n" % user_team.rating
    stats += "Wins: %s\n" % user_team.wins
    print "printing wins"
    stats += "Losses: %s\n" % user_team.losses
    print "current_streak b"
    stats += "Current Streak: %s %s\n" % (abs(user_team.current_streak), streak_suffix)
    print "current_streak a"
    stats += "Longest Winning Streak: %s\n" % user_team.longest_win_streak
    print "current_streak l"
    stats += "Longest Losing Streak: %s\n" % user_team.longest_loss_streak
    print "got stats"

    stats += "Brought to you by Nike.\n Just do it"
    # stats for a competition
    return HttpResponse(createSmsResponse(stats))

# sections[1] = competition name
# sections[2] = partner username
def handle_rank(number, sections):
    print "ranking..."
    competition_name = sections[0]

    # check if the user is registered                        
    try:
        user = Player.objects.get(phone_number=number)
        # user is registered
    except:
        # user is not registered
        return HttpResponse(createSmsResponse("Join Undisputed by texting: join undisputed MyUsername MyFirstName MyLastName"))

    # check if the competition exists
    try:
        league = League.objects.get(shorthand_name=competition_name)
    except:
        league = League.objects.get(name=competition_name)
    teams = Team.objects.filter(league=league).order_by("rating").all().reverse()

    print "get rankings for a solo competition"
    present = False
    for team in teams:
        if user.username == team.members.username:
            present = True
            break

    if not present:
        return HttpResponse(createSmsResponse("You are not registered in %s. Please try again." % competition_name))

    print "build up a string of rankings to return"
    print league
    rankings = "{0} Rankings\n".format(str(league))
    print rankings
    count = 0
    # return rankings for at most 10 teams, while making sure that we don't exceed the twilio character limit
    for count in range(min(10, len(teams))):
        # TODO: add some defense against people with really long names
        # build up the next ranking entry
        team = teams[count]
        next_entry = '%s. %s (%s) %s-%s\n' % (count + 1, team.name, team.rating, team.wins, team.losses)
        print next_entry
        # if it fits, add it to the response string
        if len(next_entry) + len(rankings) < 160:
            rankings += next_entry
        else:
            break
    print "got rankings"
    return HttpResponse(createSmsResponse(rankings))

# beat opponent1 (and opponent2 with partner )in competition_name
# sections[1] = loser1
# sections[-1] = competition name
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


    # check if the result is just a competition
    competition_name = sections[-1]
    print "competition_nameaa:%s" % competition_name
    try:
        try:
            league = League.objects.get(shorthand_name=competition_name)
        except:
            league = League.objects.get(name=competition_name)
        print league
    except NameError as e:
        print e.strerror
    print "got competition"
    # except:
    #     #TODO: implement this
    #     return HttpResponse(createSmsResponse(competition_name + " does not exist. This has not been implemented. Sorry"))

    # check if loser1 exists
    loser_username = sections[1]
    print 'loser: %s' % loser_username
    try:
        loser = Player.objects.get(username=loser_username)
        # loser1 exists
    except:
        # loser1 does not exist
        return HttpResponse(createSmsResponse(loser_username + " does not exist. Please try again."))
    print 'got lose'
    
    teams = Team.objects.filter(league=league)    

    # check that message was not malformed
    if len(sections) != 4:
        #TODO: implement this
        return HttpResponse(createSmsResponse('multiperson teams and multiword competitions not implemented yet'))

    # search for winner's team
    winning_team = None
    print "searching for winning members:"
    print winner
    for team in teams:
        print team.members
        if str(winner) == str(team.members):
            print "we found a winnner!"
            winning_team = team
            break

    if not winning_team:
        print "no winning team"
        new_team = Team(league=league,rating=2000)
        print "initialized"
        new_team.members = winner
        print "winner added?"
        new_team.name = winner.username
        print "error on save?"
        new_team.save()
        print "created new winning team"
        winning_team = new_team

    # search for the loser's team
    losing_team = None
    for team in teams:
        if str(loser) == str(team.members):
            losing_team = team
            break

    if not losing_team:
        new_l_team = Team(league=league,rating=2000)
        new_l_team.members = loser
        new_l_team.name = loser.username
        new_l_team.save()
        losing_team = new_l_team
    print "creating result..."
    # save the result
    #Todo- add teams to result
    new_result = Result(league=league,time=datetime.now(),winner=winning_team,loser=losing_team)
    print "result initialized?"
    new_result.save()
    print "result saved"
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
    teams = Team.objects.filter(league=league).order_by("rating").all().reverse()
    print "got teams to rank"
    print teams
    rank = 1
    for team in teams:
        team.ranking = rank
        team.save()
        rank += 1

    # # TODO: get teams using team name always?
    # print "getting teams to report to..."
    # winning_team = Team.objects.get(league=league, name=winning_team.name)
    # print "got winning team"
    # losing_team = Team.objects.get(league=league, username=losing_team.name)
    # print "got teams to report to"
    # in the case of a solo competition, send confirmation messages to both parties
    """
    client.sms.messages.create(
        to=str(loser.phone_number),
        from_=twilio_number,
        body="You were defeated by %s in %s. Your new rating is %s and you are ranked %s" % (winner.username, existing_competition.name, int(losing_team.rating), losing_team.ranking))
    """
    return HttpResponse(
        createSmsResponse(
            "Congrats! Your new rating is %s and you are ranked #%s in %s. A notification was sent to %s." % (int(winning_team.rating), int(winning_team.ranking), winning_team.league.name, loser.username)))





def player(request):
    username = request.GET.get('username')
    player = Player.objects.get(username=username)
    teams = Team.objects.filter(members=player)
    for t in teams:
        get_last_ten_results(t)

    return render_to_response('player.html', 
        {
            "player":player,
            "teams":teams

        },
        context_instance=RequestContext(request))# Create your views here.

def get_last_ten_results(team):
    results = Result.objects.filter(league=team.league)
    team.last_results.clear()
    results.reverse()
    team_results = []
    count = 0
    for r in results:
        if r.winner == team or r.loser == team:
            team.last_results.add(r)
            count += 1
            if count >= 10:
                break

    team.save()

def home(request):
    competitions = Competition.objects.all()
    rankings = []
    for c in competitions:
        competition_ranking = []
        teams = Team.objects.filter(competition=c).order_by("rating").all().reverse()
        rankings.append(teams)
    print rankings
    return render_to_response('home.html', 
        {
            "competitions":competitions,
            "rankings":rankings

        },
        context_instance=RequestContext(request))# Create your views here.



