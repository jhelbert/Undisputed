# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding field 'Team.ranking'
        db.add_column('main_team', 'ranking', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Team.wins'
        db.add_column('main_team', 'wins', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Team.losses'
        db.add_column('main_team', 'losses', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Team.current_streak'
        db.add_column('main_team', 'current_streak', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Team.longest_streak'
        db.add_column('main_team', 'longest_streak', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Deleting field 'Team.ranking'
        db.delete_column('main_team', 'ranking')

        # Deleting field 'Team.wins'
        db.delete_column('main_team', 'wins')

        # Deleting field 'Team.losses'
        db.delete_column('main_team', 'losses')

        # Deleting field 'Team.current_streak'
        db.delete_column('main_team', 'current_streak')

        # Deleting field 'Team.longest_streak'
        db.delete_column('main_team', 'longest_streak')
    
    
    models = {
        'main.league': {
            'Meta': {'object_name': 'League'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'passcode': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'team_size': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.player': {
            'Meta': {'object_name': 'Player'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'request_pending': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'main.result': {
            'Meta': {'object_name': 'Result'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.League']"}),
            'loser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'loser'", 'to': "orm['main.Team']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'winner'", 'to': "orm['main.Team']"})
        },
        'main.team': {
            'Meta': {'object_name': 'Team'},
            'current_streak': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'k': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.League']"}),
            'longest_streak': ('django.db.models.fields.IntegerField', [], {}),
            'losses': ('django.db.models.fields.IntegerField', [], {}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['main.Player']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'ranking': ('django.db.models.fields.IntegerField', [], {}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '2000'}),
            'wins': ('django.db.models.fields.IntegerField', [], {})
        }
    }
    
    complete_apps = ['main']
