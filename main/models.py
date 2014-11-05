
from django.db import models

# Create your models here.

class Competition(models.Model):
	name = models.CharField(max_length=100)
	def __unicode__(self):
		return self.name
class Player(models.Model):
	username = models.CharField(max_length=30,null=True,blank=True)
	phone_number = models.CharField(max_length=20)
	name = models.CharField(max_length=30,null=True,blank=True)
	request_pending = models.BooleanField()
	def __unicode__(self):
		return self.username


class League(models.Model):
	competition = models.ForeignKey(Competition,null=True,blank=True)
	shorthand_name = models.CharField(max_length=20,null=True, blank=True)
	name = models.CharField(max_length=30)
	passcode = models.CharField(max_length=20)
	team_size = models.IntegerField()
	def __unicode__(self):
		return self.name

class Team(models.Model):
	league = models.ForeignKey(League,null=True,blank=True)
	competition = models.ForeignKey(Competition,null=True,blank=True)
	name = models.CharField(max_length=20)
	members = models.ForeignKey(Player,null=True,blank=True)
	rating = models.IntegerField(default=2000)
	k = models.IntegerField(null=True,blank=True)
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	current_streak = models.IntegerField(default=0)
	longest_win_streak = models.IntegerField(default=0)
	longest_loss_streak = models.IntegerField(default=0)
	ranking = models.IntegerField(null=True,blank=True)
	last_results = models.ManyToManyField('Result',null=True,blank=True)
	def __unicode__(self):
		return self.name

class Result(models.Model):
	league = models.ForeignKey(League)
	winner = models.ForeignKey(Team, related_name="winner",null=True,blank=True)
	loser = models.ForeignKey(Team, related_name="loser",null=True,blank=True)
	time = models.DateTimeField()
