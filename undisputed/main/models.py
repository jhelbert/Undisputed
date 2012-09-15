
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
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	current_streak = models.IntegerField(default=0)
	longest_win_streak = models.IntegerField(default=0)
	longest_loss_streak = models.IntegerField(default=0)
	ranking = models.IntegerField()
	def __unicode__(self):
		return self.name

class Result(models.Model):
	league = models.ForeignKey(League)
	winner = models.ForeignKey(Team, related_name="winner")
	loser = models.ForeignKey(Team, related_name="loser")
	time = models.DateTimeField()
