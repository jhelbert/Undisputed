# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Team.shorthand_name'
        db.delete_column('main_team', 'shorthand_name')

        # Adding field 'League.shorthand_name'
        db.add_column('main_league', 'shorthand_name',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Team.shorthand_name'
        db.add_column('main_team', 'shorthand_name',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'League.shorthand_name'
        db.delete_column('main_league', 'shorthand_name')


    models = {
        'main.competition': {
            'Meta': {'object_name': 'Competition'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.league': {
            'Meta': {'object_name': 'League'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Competition']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'passcode': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'shorthand_name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'team_size': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.player': {
            'Meta': {'object_name': 'Player'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'request_pending': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        },
        'main.result': {
            'Meta': {'object_name': 'Result'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Competition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loser': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'loser'", 'null': 'True', 'to': "orm['main.Team']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'winner'", 'null': 'True', 'to': "orm['main.Team']"})
        },
        'main.team': {
            'Meta': {'object_name': 'Team'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Competition']", 'null': 'True', 'blank': 'True'}),
            'current_streak': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'k': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last_results': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['main.Result']", 'null': 'True', 'blank': 'True'}),
            'leagues': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['main.League']", 'null': 'True', 'blank': 'True'}),
            'longest_loss_streak': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'longest_win_streak': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'losses': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'members': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Player']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'ranking': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '2000'}),
            'wins': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['main']