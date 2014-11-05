# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Competition'
        db.create_table('main_competition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('main', ['Competition'])

        # Adding model 'Player'
        db.create_table('main_player', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('request_pending', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('main', ['Player'])

        # Adding model 'League'
        db.create_table('main_league', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Competition'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('passcode', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('team_size', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('main', ['League'])

        # Adding model 'Team'
        db.create_table('main_team', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Competition'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('members', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Player'], null=True, blank=True)),
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=2000)),
            ('k', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('wins', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('losses', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('current_streak', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('longest_win_streak', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('longest_loss_streak', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('ranking', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('main', ['Team'])

        # Adding M2M table for field leagues on 'Team'
        m2m_table_name = db.shorten_name('main_team_leagues')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm['main.team'], null=False)),
            ('league', models.ForeignKey(orm['main.league'], null=False))
        ))
        db.create_unique(m2m_table_name, ['team_id', 'league_id'])

        # Adding M2M table for field last_results on 'Team'
        m2m_table_name = db.shorten_name('main_team_last_results')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm['main.team'], null=False)),
            ('result', models.ForeignKey(orm['main.result'], null=False))
        ))
        db.create_unique(m2m_table_name, ['team_id', 'result_id'])

        # Adding model 'Result'
        db.create_table('main_result', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Competition'])),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='winner', null=True, to=orm['main.Team'])),
            ('loser', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='loser', null=True, to=orm['main.Team'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('main', ['Result'])


    def backwards(self, orm):
        # Deleting model 'Competition'
        db.delete_table('main_competition')

        # Deleting model 'Player'
        db.delete_table('main_player')

        # Deleting model 'League'
        db.delete_table('main_league')

        # Deleting model 'Team'
        db.delete_table('main_team')

        # Removing M2M table for field leagues on 'Team'
        db.delete_table(db.shorten_name('main_team_leagues'))

        # Removing M2M table for field last_results on 'Team'
        db.delete_table(db.shorten_name('main_team_last_results'))

        # Deleting model 'Result'
        db.delete_table('main_result')


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