# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TaskInvalidationCriteria'
        db.create_table('tasks_taskinvalidationcriteria', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field_name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('field_value', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('relation', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('tasks', ['TaskInvalidationCriteria'])

        # Adding model 'TaskExternalItem'
        db.create_table('tasks_taskexternalitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('tasks', ['TaskExternalItem'])

        # Adding model 'TaskImportBatch'
        db.create_table('tasks_taskimportbatch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('query', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.TaskTemplate'])),
        ))
        db.send_create_signal('tasks', ['TaskImportBatch'])

        # Adding M2M table for field invalidation_criteria on 'TaskImportBatch'
        m2m_table_name = db.shorten_name('tasks_taskimportbatch_invalidation_criteria')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('taskimportbatch', models.ForeignKey(orm['tasks.taskimportbatch'], null=False)),
            ('taskinvalidationcriteria', models.ForeignKey(orm['tasks.taskinvalidationcriteria'], null=False))
        ))
        db.create_unique(m2m_table_name, ['taskimportbatch_id', 'taskinvalidationcriteria_id'])

        # Adding model 'BugzillaBug'
        db.create_table('tasks_bugzillabug', (
            ('taskexternalitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['tasks.TaskExternalItem'], unique=True, primary_key=True)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('bugzilla_id', self.gf('django.db.models.fields.IntegerField')(unique=True, max_length=20)),
        ))
        db.send_create_signal('tasks', ['BugzillaBug'])

        # Adding model 'TaskTemplate'
        db.create_table('tasks_tasktemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.TaskProject'], null=True, blank=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.TaskTeam'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.TaskType'], null=True, blank=True)),
            ('difficulty', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('execution_time', self.gf('django.db.models.fields.IntegerField')(default=15)),
            ('instructions', self.gf('django.db.models.fields.TextField')()),
            ('is_draft', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_valid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('prerequisites', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('repeatable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('short_description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('why_this_matters', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('tasks', ['TaskTemplate'])


        # Changing field 'TaskAttempt.user'
        db.alter_column('tasks_taskattempt', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.SET_NULL))
        # Adding field 'Task.is_valid'
        db.add_column('tasks_task', 'is_valid',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Task.external_item'
        db.add_column('tasks_task', 'external_item',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.TaskExternalItem'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Task.batch'
        db.add_column('tasks_task', 'batch',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.TaskImportBatch'], null=True, blank=True),
                      keep_default=False)


        # Changing field 'Task.creator'
        db.alter_column('tasks_task', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))
        # Adding field 'TaskKeyword.task_template'
        db.add_column('tasks_taskkeyword', 'task_template',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='keyword_set', null=True, to=orm['tasks.TaskTemplate']),
                      keep_default=False)


        # Changing field 'TaskKeyword.task'
        db.alter_column('tasks_taskkeyword', 'task_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['tasks.Task']))

        # Changing field 'TaskKeyword.creator'
        db.alter_column('tasks_taskkeyword', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'TaskType.creator'
        db.alter_column('tasks_tasktype', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'TaskTeam.creator'
        db.alter_column('tasks_taskteam', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'TaskProject.creator'
        db.alter_column('tasks_taskproject', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

    def backwards(self, orm):
        # Deleting model 'TaskInvalidationCriteria'
        db.delete_table('tasks_taskinvalidationcriteria')

        # Deleting model 'TaskExternalItem'
        db.delete_table('tasks_taskexternalitem')

        # Deleting model 'TaskImportBatch'
        db.delete_table('tasks_taskimportbatch')

        # Removing M2M table for field invalidation_criteria on 'TaskImportBatch'
        db.delete_table(db.shorten_name('tasks_taskimportbatch_invalidation_criteria'))

        # Deleting model 'BugzillaBug'
        db.delete_table('tasks_bugzillabug')

        # Deleting model 'TaskTemplate'
        db.delete_table('tasks_tasktemplate')


        # Changing field 'TaskAttempt.user'
        db.alter_column('tasks_taskattempt', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User']))
        # Deleting field 'Task.is_valid'
        db.delete_column('tasks_task', 'is_valid')

        # Deleting field 'Task.external_item'
        db.delete_column('tasks_task', 'external_item_id')

        # Deleting field 'Task.batch'
        db.delete_column('tasks_task', 'batch_id')


        # Changing field 'Task.creator'
        db.alter_column('tasks_task', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User']))
        # Deleting field 'TaskKeyword.task_template'
        db.delete_column('tasks_taskkeyword', 'task_template_id')


        # Changing field 'TaskKeyword.task'
        db.alter_column('tasks_taskkeyword', 'task_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['tasks.Task']))

        # Changing field 'TaskKeyword.creator'
        db.alter_column('tasks_taskkeyword', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User']))

        # Changing field 'TaskType.creator'
        db.alter_column('tasks_tasktype', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User']))

        # Changing field 'TaskTeam.creator'
        db.alter_column('tasks_taskteam', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User']))

        # Changing field 'TaskProject.creator'
        db.alter_column('tasks_taskproject', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User']))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tasks.bugzillabug': {
            'Meta': {'object_name': 'BugzillaBug', '_ormbases': ['tasks.TaskExternalItem']},
            'bugzilla_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'max_length': '20'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'taskexternalitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['tasks.TaskExternalItem']", 'unique': 'True', 'primary_key': 'True'})
        },
        'tasks.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'attempt': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskAttempt']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'tasks.task': {
            'Meta': {'object_name': 'Task'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskImportBatch']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'difficulty': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'execution_time': ('django.db.models.fields.IntegerField', [], {'default': '15'}),
            'external_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskExternalItem']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructions': ('django.db.models.fields.TextField', [], {}),
            'is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'prerequisites': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskProject']", 'null': 'True', 'blank': 'True'}),
            'repeatable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'short_description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskTeam']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskType']", 'null': 'True', 'blank': 'True'}),
            'why_this_matters': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'tasks.taskattempt': {
            'Meta': {'ordering': "['-modified']", 'object_name': 'TaskAttempt'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        'tasks.taskexternalitem': {
            'Meta': {'object_name': 'TaskExternalItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'tasks.taskimportbatch': {
            'Meta': {'object_name': 'TaskImportBatch'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation_criteria': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tasks.TaskInvalidationCriteria']", 'symmetrical': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'query': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskTemplate']"})
        },
        'tasks.taskinvalidationcriteria': {
            'Meta': {'object_name': 'TaskInvalidationCriteria'},
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'field_value': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relation': ('django.db.models.fields.IntegerField', [], {})
        },
        'tasks.taskkeyword': {
            'Meta': {'object_name': 'TaskKeyword'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'keyword_set'", 'null': 'True', 'to': "orm['tasks.Task']"}),
            'task_template': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'keyword_set'", 'null': 'True', 'to': "orm['tasks.TaskTemplate']"})
        },
        'tasks.taskproject': {
            'Meta': {'object_name': 'TaskProject'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'tasks.taskteam': {
            'Meta': {'object_name': 'TaskTeam'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'tasks.tasktemplate': {
            'Meta': {'object_name': 'TaskTemplate'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'difficulty': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'execution_time': ('django.db.models.fields.IntegerField', [], {'default': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructions': ('django.db.models.fields.TextField', [], {}),
            'is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'prerequisites': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskProject']", 'null': 'True', 'blank': 'True'}),
            'repeatable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'short_description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskTeam']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskType']", 'null': 'True', 'blank': 'True'}),
            'why_this_matters': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'tasks.tasktype': {
            'Meta': {'object_name': 'TaskType'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['tasks']