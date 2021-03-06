import re, os, cgi, hashlib, urllib2, json, base64, hmac, hmac, sha
from subprocess import *
from datetime import *
from random import choice

import twilio.twiml
from twilio.rest import TwilioRestClient

from main.models import Player, Team, Result, Competition, League
import settings

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
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.contrib import auth
from django.core.mail import send_mail, EmailMessage

from xml.dom.minidom import getDOMImplementation,parse,parseString


# twilio account information
TWILIO_ACCOUNT_SID = "AC4854286859444a07a57dfdc44c8eecea"
TWILIO_AUTH_TOKEN = "e0f79b613153fb5b2525f7552ef8cd1f"


# client used to send messages
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

COMMANDS_MSG = "commands: \n  beat <player> \n lost to <player> \n  rankings\n  my stats"

def get_object(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

@csrf_exempt
def incoming_text(request):
    league_from_number = request.GET.get('league')

    league = None
    if league_from_number:
        league = League.objects.get(shorthand_name=league_from_number)

    number = request.GET.get('From')
    msg = request.GET.get('Body').lower().replace('\n', '')
    sections = msg.split(" ")

    try:
        player = Player.objects.get(phone_number=number)
        if not player.username:
            player.username = msg
            player.save()
            return HttpResponse(createSmsResponse(COMMANDS_MSG))
    except:
        player = Player(phone_number=number)
        player.save()
        if league:
            return HttpResponse(createSmsResponse("Welcome to {0} on Undisputed. Enter your initials.".format(league.name)))
        else:
            return HttpResponse(createSmsResponse("Welcome to Undisputed. Enter your initials."))

    # join undisputed username firstname lastname
    # TODO- all other valid characters, regex check on each section

    if re.match("^me$",msg):
        return handle_me(number)
    # options
    elif re.match("^options$",msg):
        return HttpResponse(createSmsResponse(COMMANDS_MSG))

    elif re.match("^lost to [a-zA-z0-9_]+$", msg) and league_from_number:
        sections = [sections[0], sections[2], "in", league_from_number]
        return handle_win(number, sections, True)

    elif re.match("^beat [a-zA-z0-9_]+$", msg) and league_from_number:
        sections = sections + ["in", league_from_number]
        return handle_win(number, sections)

    # beat opponent1 (and opponent2 with partner )in competition_name
    elif re.match("^beat [a-zA-z0-9_]+ (and [a-zA-z0-9_]+ with [a-zA-z0-9_]+ )?in [a-zA-z0-9_]+$", msg):
        return handle_win(number, sections)

    # competition_name rankings
    elif re.match("^rankings$", msg) and league_from_number:
        sections = [league_from_number] + sections
        return handle_rank(number,sections)

    # competition_name rankings
    elif re.match("^[a-zA-z0-9_]+ rankings$", msg):
        return handle_rank(number,sections)

    # my competition_name stats
    elif re.match("^my stats$", msg) and league_from_number:
        sections = ['my', league_from_number, 'stats']
        return handle_stats(number,sections)

    # my competition_name stats
    elif re.match("^my [a-zA-z0-9_]+( [a-zA-z0-9_]+)? stats$", msg):
        sections = msg.split(" ")

        return handle_stats(number,sections)

     # create solo|partner|partnered league name password
    # TODO: league name multiple words?
    elif re.match("^create (solo|partnered|partner) league [a-zA-Z0-9_]+ [a-zA-Z0-9_]+$", msg):
        return handle_create_league(number, sections)

    # join league_name password (with partner):
    elif re.match("^join [a-zA-Z0-9_]+ [a-zA-Z0-9_]+( with [a-zA-Z ]+)?$",msg):
        return handle_join_league(number, sections)

    else:
        return HttpResponse(createSmsResponse("Not recognized. Text 'options' to view your options."))

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


def handle_join_undisputed(number, sections):
    username = sections[2]
    name = " ".join(sections[3:])

    # check if the account already exists
    try:
        player = Player.objects.get(phone_number=number)
        return HttpResponse(createSmsResponse("You have already created an account with username %s" % player.username))
    except:
        pass

    # trying to make an account
    try:
        existing_player = Player.objects.get(username=username)
        # username taken
        return HttpResponse(createSmsResponse("username %s already taken, please try another one" % username))
    except:
        # making account
        new_player = Player.objects.create(name=name,username=username,phone_number=number)
        return HttpResponse(createSmsResponse("Welcome, here are your options:\n" + options))

def handle_stats(number, sections):
    # check if player is registered
    try:
        user = Player.objects.get(phone_number=number)
    except:
        return HttpResponse(createSmsResponse("You aren't on Undisputed. To join:\n join undisputed MyUsername MyFirstName MyLastName"))

    # check if competition exists
    competition_name = sections[1]
    try:
        try:
            league = League.objects.get(shorthand_name=competition_name)
        except:
            league = League.objects.get(name=competition_name)
    except:
        return HttpResponse(createSmsResponse(competition_name + " does not exist. Please try again."))

    teams = Team.objects.filter(league=league).all()

    user_team = get_object(Team, name=user.username)

    # the user's team does not exist
    if not user_team:
        return HttpResponse(createSmsResponse("You are not a registered team in " + competition_name + "."))

    # determine the suffix for the win streak


    # build up the return string
    stats =  "Rank: %s / %s\n" % (user_team.ranking, len(teams))
    stats += "Rating: %s\n" % user_team.rating
    stats += "W: %s\t" % user_team.wins
    stats += "L: %s\n" % user_team.losses
    stats += "Current Streak: %s %s\n" % (abs(user_team.current_streak), user_team.streak_suffix())
    stats += "Longest Win Streak: %s\n" % user_team.longest_win_streak
    stats += "Longest Loss Streak: %s\n" % user_team.longest_loss_streak
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
    for count in range(len(teams)):
        # TODO: add some defense against people with really long names
        # build up the next ranking entry
        team = teams[count]
        next_entry = '%s. %s (%s) %s-%s\n' % (count + 1, team.name.upper(), team.rating, team.wins, team.losses)
        print next_entry
        # if it fits, add it to the response string
        #if len(next_entry) + len(rankings) < 160:
        rankings += next_entry

    print "got rankings"
    return HttpResponse(createSmsResponse(rankings))

# beat opponent1 (and opponent2 with partner )in competition_name
# sections[1] = loser1
# sections[-1] = competition name
# if partnered:
#    sections[3] = loser2
#    sections[5] = partner
def handle_win(number, sections, loser_submit=False):
    # check that both players exist in system
    winner = get_object(Player, phone_number=number)
    if not winner:
        return HttpResponse(createSmsResponse("Join Undisputed first"))

    loser_username = sections[1]
    loser = get_object(Player, username=loser_username)
    if not loser:
        return HttpResponse(createSmsResponse(loser_username + " does not exist. Please try again."))


    # check if the result is just a competition
    competition_name = sections[-1]
    league = get_object(League, shorthand_name=competition_name)
    if not league:
        league = get_object(League, name=competition_name)

    # if this flag is true, swap
    if loser_submit:
        temp = winner
        winner = loser
        loser = temp

    teams = Team.objects.filter(league=league)

    # check that message was not malformed
    if len(sections) != 4:
        return HttpResponse(createSmsResponse('multiperson teams and multiword competitions not implemented yet'))

    # search for existing teams
    winning_team = get_object(Team, name=winner.username)
    losing_team = get_object(Team, name=loser.username)

    if not winning_team:
        new_team = Team(league=league,rating=2000,ranking=100, name=winner.username)
        new_team.members = winner
        new_team.name = winner.username
        new_team.save()
        winning_team = new_team

    # search for the loser's team

    if not losing_team:
        new_l_team = Team(league=league,rating=2000, ranking=100)
        new_l_team.members = loser
        new_l_team.name = loser.username
        new_l_team.save()
        losing_team = new_l_team

    # save the result
    #Todo- add teams to results
    new_result = Result.objects.create(league=league,time=datetime.now(),winner=winning_team,loser=losing_team)

    # use Elo's algorithm to calculate the new ratings
    calculate_elo_update(winning_team, losing_team)

    # update each team's streaks
    winning_team.update_streak(True)
    losing_team.update_streak(False)

    # use the new ratings to calculate new rankings
    teams = Team.objects.filter(league=league).order_by("rating").all().reverse()
    rank = 1
    for team in teams:
        team.ranking = rank
        team.save()
        rank += 1


    winning_team = Team.objects.get(name=winner.username)
    losing_team = Team.objects.get(name=loser.username)

    NOTIFICATIONS = True

    loser_string = "You were defeated by %s in %s. Your new rating is %s and you are ranked %s" % (winner.username.upper(), league.name, int(losing_team.rating), losing_team.ranking)
    winner_string =  "Congrats on beating %s! Your new rating is %s and you are ranked #%s in %s. A notification was sent to %s." % (loser.username.upper(), int(winning_team.rating), int(winning_team.ranking), winning_team.league.name, loser.username.upper())

    if loser_submit:
        to_msg = winner_string
        return_msg = loser_string
        to_phone_number = winner.phone_number
    else:
        to_msg = loser_string
        return_msg = winner_string
        to_phone_number = loser.phone_number

    if competition_name == "ksfifa":
        TWILIO_NUMBER = "+19786730440"
    elif competition_name == "kspingpong":
        TWILIO_NUMBER = "+14793163917"

    if NOTIFICATIONS:
        client.sms.messages.create(
            to=str(to_phone_number),
            from_=TWILIO_NUMBER,
            body=to_msg)

    return HttpResponse(
        createSmsResponse(return_msg
           ))



def calculate_elo_update(winning_team, losing_team):
    ELO_SPREAD = 1000.0
    ELO_VOLATILITY = 80.0

    old_winner_rating = winning_team.rating
    old_loser_rating = losing_team.rating

    q_winner = 10**(old_winner_rating / ELO_SPREAD)
    q_loser = 10**(old_loser_rating / ELO_SPREAD)
    expected_winner = q_winner / (q_winner + q_loser)
    expected_loser = q_loser / (q_winner + q_loser)

    winning_team.rating = old_winner_rating + ELO_VOLATILITY * (1 - expected_winner)
    losing_team.rating = old_loser_rating + ELO_VOLATILITY * (0 - expected_loser)

    winning_team.save()
    losing_team.save()



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
    return render_to_response('home.html',
        {
            "competitions":competitions,
            "rankings":rankings
        },
        context_instance=RequestContext(request))