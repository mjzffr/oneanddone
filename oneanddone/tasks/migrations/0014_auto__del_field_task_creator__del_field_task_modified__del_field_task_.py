# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Task.creator'
        db.delete_column('tasks_task', 'creator_id')

        # Deleting field 'Task.modified'
        db.delete_column('tasks_task', 'modified')

        # Deleting field 'Task.id'
        db.delete_column('tasks_task', 'id')

        # Deleting field 'Task.is_valid'
        db.delete_column('tasks_task', 'is_valid')

        # Deleting field 'Task.short_description'
        db.delete_column('tasks_task', 'short_description')

        # Deleting field 'Task.type'
        db.delete_column('tasks_task', 'type_id')

        # Deleting field 'Task.start_date'
        db.delete_column('tasks_task', 'start_date')

        # Deleting field 'Task.end_date'
        db.delete_column('tasks_task', 'end_date')

        # Deleting field 'Task.execution_time'
        db.delete_column('tasks_task', 'execution_time')

        # Deleting field 'Task.difficulty'
        db.delete_column('tasks_task', 'difficulty')

        # Deleting field 'Task.repeatable'
        db.delete_column('tasks_task', 'repeatable')

        # Deleting field 'Task.is_draft'
        db.delete_column('tasks_task', 'is_draft')

        # Deleting field 'Task.instructions'
        db.delete_column('tasks_task', 'instructions')

        # Deleting field 'Task.name'
        db.delete_column('tasks_task', 'name')

        # Deleting field 'Task.why_this_matters'
        db.delete_column('tasks_task', 'why_this_matters')

        # Deleting field 'Task.created'
        db.delete_column('tasks_task', 'created')

        # Deleting field 'Task.prerequisites'
        db.delete_column('tasks_task', 'prerequisites')

        # Deleting field 'Task.project'
        db.delete_column('tasks_task', 'project_id')

        # Deleting field 'Task.team'
        db.delete_column('tasks_task', 'team_id')


        # Changing field 'Task.task_template'
        db.alter_column('tasks_task', 'task_template_id', self.gf('django.db.models.fields.related.OneToOneField')(default=None, to=orm['tasks.TaskTemplate'], unique=True, primary_key=True))
        # Adding field 'TaskKeyword.task_backup'
        db.add_column('tasks_taskkeyword', 'task_backup',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.TaskTemplate'], null=True, blank=True),
                      keep_default=False)


        # Changing field 'TaskKeyword.task'
        db.alter_column('tasks_taskkeyword', 'task_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.TaskTemplate']))

    def backwards(self, orm):
        # Adding field 'Task.creator'
        db.add_column('tasks_task', 'creator',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Task.modified'
        db.add_column('tasks_task', 'modified',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2014, 7, 21, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'Task.id'
        db.add_column('tasks_task', 'id',
                      self.gf('django.db.models.fields.AutoField')(default=None, primary_key=True),
                      keep_default=False)

        # Adding field 'Task.is_valid'
        db.add_column('tasks_task', 'is_valid',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Task.short_description'
        db.add_column('tasks_task', 'short_description',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding field 'Task.type'
        db.add_column('tasks_task', 'type',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.TaskType'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Task.start_date'
        db.add_column('tasks_task', 'start_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Task.end_date'
        db.add_column('tasks_task', 'end_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Task.execution_time'
        db.add_column('tasks_task', 'execution_time',
                      self.gf('django.db.models.fields.IntegerField')(default=15),
                      keep_default=False)

        # Adding field 'Task.difficulty'
        db.add_column('tasks_task', 'difficulty',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Task.repeatable'
        db.add_column('tasks_task', 'repeatable',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Task.is_draft'
        db.add_column('tasks_task', 'is_draft',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Task.instructions'
        db.add_column('tasks_task', 'instructions',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Task.name'
        db.add_column('tasks_task', 'name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding field 'Task.why_this_matters'
        db.add_column('tasks_task', 'why_this_matters',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Task.created'
        db.add_column('tasks_task', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2014, 7, 21, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'Task.prerequisites'
        db.add_column('tasks_task', 'prerequisites',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Task.project'
        db.add_column('tasks_task', 'project',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.TaskProject'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Task.team'
        db.add_column('tasks_task', 'team',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['tasks.TaskTeam']),
                      keep_default=False)


        # Changing field 'Task.task_template'
        db.alter_column('tasks_task', 'task_template_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['tasks.TaskTemplate'], unique=True, null=True))
        # Deleting field 'TaskKeyword.task_backup'
        db.delete_column('tasks_taskkeyword', 'task_backup_id')


        # Changing field 'TaskKeyword.task'
        db.alter_column('tasks_taskkeyword', 'task_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task']))

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
            'Meta': {'object_name': 'BugzillaBug', '_ormbases': ['tasks.TaskImportedInfo']},
            'bugzilla_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'max_length': '20'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'taskimportedinfo_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['tasks.TaskImportedInfo']", 'unique': 'True', 'primary_key': 'True'})
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
            'Meta': {'object_name': 'Task', '_ormbases': ['tasks.TaskTemplate']},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskImportBatch']", 'null': 'True', 'blank': 'True'}),
            'external_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskImportedInfo']", 'null': 'True', 'blank': 'True'}),
            'task_template': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['tasks.TaskTemplate']", 'unique': 'True', 'primary_key': 'True'})
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
        'tasks.taskimportbatch': {
            'Meta': {'object_name': 'TaskImportBatch'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'query': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskTemplate']"})
        },
        'tasks.taskimportedinfo': {
            'Meta': {'object_name': 'TaskImportedInfo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'tasks.taskinvalidationcriterion': {
            'Meta': {'object_name': 'TaskInvalidationCriterion'},
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'field_value': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relation': ('django.db.models.fields.IntegerField', [], {}),
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskImportBatch']"})
        },
        'tasks.taskkeyword': {
            'Meta': {'object_name': 'TaskKeyword'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'keyword_set'", 'to': "orm['tasks.TaskTemplate']"}),
            'task_backup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.TaskTemplate']", 'null': 'True', 'blank': 'True'})
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
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
