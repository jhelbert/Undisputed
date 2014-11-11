
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
		if self.username:
			return self.username
		return "No name"


class League(models.Model):
	competition = models.ForeignKey(Competition,null=True,blank=True)
	shorthand_name = models.CharField(max_length=20,null=True, blank=True)
	name = models.CharField(max_length=30)
	passcode = models.CharField(max_length=20)
	team_size = models.IntegerField()
	def __unicode__(self):
		return self.name

	def replay_results(self):
		# initialize players to 2000
		for team in self.teams.all():
			team.rating = 2000
			team.save()
		results = Result.objects.filter(league=self)
		for result in results:
			result.update_elo()
		
		print results






class Team(models.Model):
	league = models.ForeignKey(League,null=True,blank=True, related_name='teams')
	competition = models.ForeignKey(Competition,null=True,blank=True)
	name = models.CharField(max_length=20)
	members = models.ForeignKey(Player,null=True,blank=True)
	rating = models.IntegerField(default=2000)
	global_rating = models.IntegerField(default=2000)
	k = models.IntegerField(null=True,blank=True)
	current_streak = models.IntegerField(default=0)
	longest_win_streak = models.IntegerField(default=0)
	longest_loss_streak = models.IntegerField(default=0)
	ranking = models.IntegerField(null=True,blank=True)
	last_results = models.ManyToManyField('Result',null=True,blank=True)

	def __unicode__(self):
		return self.name

	def _wins(self):
		return len(Result.objects.filter(winner=self).all())
	wins = property(_wins)

	def _losses(self):
		return len(Result.objects.filter(loser=self).all())
	losses = property(_losses)

	def update_streak(self, is_win):
		if is_win:
			if self.current_streak > 0:
				self.current_streak += 1
			else:
				self.current_streak = 1
			self.longest_win_streak = max(self.longest_win_streak,self.current_streak)

		else:
			if self.current_streak < 0:
				self.current_streak -= 1
			else:
				self.current_streak = -1
			self.longest_loss_streak = min(self.longest_loss_streak,self.current_streak)

		self.save()

	def streak_suffix(self):
		if self.current_streak > 1 or not self.current_streak:
			return "wins"
		elif self.current_streak == 1:
			return "win"
		elif self.current_streak == -1:
			return "loss"
		else:
			return "losses"

class Result(models.Model):
	league = models.ForeignKey(League)
	winner = models.ForeignKey(Team, related_name="winner",null=True,blank=True)
	loser = models.ForeignKey(Team, related_name="loser",null=True,blank=True)
	time = models.DateTimeField()

	def update_elo(self, global_update=False):
		ELO_SPREAD = 1000.0
		ELO_VOLATILITY = 80.0

		if global_update:
			winner_rating = self.winner.global_rating
			loser_rating = self.loser.global_rating
		else:
			winner_rating = self.winner.rating  
			loser_rating = self.loser.rating

		q_winner = 10**(winner_rating / ELO_SPREAD)
		q_loser = 10**(loser_rating / ELO_SPREAD)
		expected_winner = q_winner / (q_winner + q_loser)
		expected_loser = q_loser / (q_winner + q_loser)

		# update step
		if global_update:
			self.winner.global_rating = winner_rating + ELO_VOLATILITY * (1 - expected_winner)
			self.loser.global_rating = loser_rating + ELO_VOLATILITY * (0 - expected_loser)
		else:
			self.winner.rating = winner_rating + ELO_VOLATILITY * (1 - expected_winner)
			self.loser.rating = loser_rating + ELO_VOLATILITY * (0 - expected_loser)

		self.winner.save()
		self.loser.save()

		if not global_update:
			self.update_elo(global_update=True)

	def __unicode__(self):
 		return "{0} beat {1} - {2}".format(self.winner, self.loser, self.time)
