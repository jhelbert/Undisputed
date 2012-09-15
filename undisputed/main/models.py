from django.db import models

# Create your models here.
class Player(models.Model):
	username = models.CharField(max_length=30)
	phone_number = models.CharField(max_length=20)
	name = models.CharField(max_length=30)

class League(models.Model):
	name = models.CharField(max_length=30)
	passcode = models.CharField(max_length=20)

class Team(models.Model):
	league = models.ForeignKey(League)
	name = models.CharField(max_length=20)
	members = models.ManyToManyField(Player)
	rating = models.IntegerField()
	k = models.IntegerField()

class Result(models.Model):
	league = models.ForeignKey(League)
	winning_team = models.ForeignKey(Team, related_name="winning_team")
	losing_team = models.ForeignKey(Team, related_name="losing_team")
	time = models.DateTimeField()
	confirmed = models.BooleanField()