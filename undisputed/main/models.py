
from django.db import models

# Create your models here.
class Player(models.Model):
	username = models.CharField(max_length=30)
	phone_number = models.CharField(max_length=20)
	name = models.CharField(max_length=30)
	request_pending = models.BooleanField()
	def __unicode__(self):
		return self.name

class League(models.Model):
	name = models.CharField(max_length=30)
	passcode = models.CharField(max_length=20)
	team_size = models.IntegerField()
	def __unicode__(self):
		return self.name

class Team(models.Model):
	league = models.ForeignKey(League)
	name = models.CharField(max_length=20)
	members = models.ManyToManyField(Player,null=True,blank=True)
	rating = models.IntegerField(default=2000)
	k = models.IntegerField(null=True,blank=True)
	wins = models.IntegerField()
	losses = models.IntegerField()
	current_streak = models.IntegerField()
	longest_streak = models.IntegerField()
	ranking = models.IntegerField()
	def __unicode__(self):
		return self.name

class Result(models.Model):
	league = models.ForeignKey(League)
	winner = models.ForeignKey(Team, related_name="winner")
	loser = models.ForeignKey(Team, related_name="loser")
	time = models.DateTimeField()
