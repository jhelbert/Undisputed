# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Player'
        db.create_table('main_player', (
            ('username', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('main', ['Player'])

        # Adding model 'League'
        db.create_table('main_league', (
            ('passcode', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('main', ['League'])

        # Adding model 'Team'
        db.create_table('main_team', (
            ('league', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.League'])),
            ('k', self.gf('django.db.models.fields.IntegerField')()),
            ('rating', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('main', ['Team'])

        # Adding M2M table for field members on 'Team'
        db.create_table('main_team_members', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm['main.team'], null=False)),
            ('player', models.ForeignKey(orm['main.player'], null=False))
        ))
        db.create_unique('main_team_members', ['team_id', 'player_id'])

        # Adding model 'Result'
        db.create_table('main_result', (
            ('league', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.League'])),
            ('confirmed', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('losing_team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='losing_team', to=orm['main.Team'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('winning_team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='winning_team', to=orm['main.Team'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('main', ['Result'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Player'
        db.delete_table('main_player')

        # Deleting model 'League'
        db.delete_table('main_league')

        # Deleting model 'Team'
        db.delete_table('main_team')

        # Removing M2M table for field members on 'Team'
        db.delete_table('main_team_members')

        # Deleting model 'Result'
        db.delete_table('main_result')
    
    
    models = {
        'main.league': {
            'Meta': {'object_name': 'League'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'passcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'main.player': {
            'Meta': {'object_name': 'Player'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'main.result': {
            'Meta': {'object_name': 'Result'},
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.League']"}),
            'losing_team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'losing_team'", 'to': "orm['main.Team']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'winning_team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'winning_team'", 'to': "orm['main.Team']"})
        },
        'main.team': {
            'Meta': {'object_name': 'Team'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'k': ('django.db.models.fields.IntegerField', [], {}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.League']"}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Player']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'rating': ('django.db.models.fields.IntegerField', [], {})
        }
    }
    
    complete_apps = ['main']
