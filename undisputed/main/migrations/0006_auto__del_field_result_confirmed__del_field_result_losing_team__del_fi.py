# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting field 'Result.confirmed'
        db.delete_column('main_result', 'confirmed')

        # Deleting field 'Result.losing_team'
        db.delete_column('main_result', 'losing_team_id')

        # Deleting field 'Result.winning_team'
        db.delete_column('main_result', 'winning_team_id')

        # Adding field 'Result.winner'
        db.add_column('main_result', 'winner', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='winner', to=orm['main.Team']), keep_default=False)

        # Adding field 'Result.loser'
        db.add_column('main_result', 'loser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='loser', to=orm['main.Team']), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Adding field 'Result.confirmed'
        db.add_column('main_result', 'confirmed', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'Result.losing_team'
        db.add_column('main_result', 'losing_team', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='losing_team', to=orm['main.Team']), keep_default=False)

        # Adding field 'Result.winning_team'
        db.add_column('main_result', 'winning_team', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='winning_team', to=orm['main.Team']), keep_default=False)

        # Deleting field 'Result.winner'
        db.delete_column('main_result', 'winner_id')

        # Deleting field 'Result.loser'
        db.delete_column('main_result', 'loser_id')
    
    
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'k': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.League']"}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['main.Player']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }
    
    complete_apps = ['main']
