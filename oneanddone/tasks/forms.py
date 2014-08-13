# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django import forms
#from django.forms.formsets import BaseFormSet, formset_factory

from django_ace import AceWidget
from tower import ugettext as _

from oneanddone.tasks.bugzilla import request_bugcount
from oneanddone.tasks.models import Feedback, Task, TaskImportBatch, TaskInvalidationCriterion
from oneanddone.tasks.widgets import CalendarInput, HorizRadioSelect


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('text',)


class TaskInvalidationCriterionForm(forms.ModelForm):
    #def save(self, *args, **kwargs):
        # TODO mzf is this needed?
    #    return super(TaskInvalidationCriterionForm, self).save(*args, **kwargs)

    class Meta:
        model = TaskInvalidationCriterion
        fields = ('field_name', 'relation', 'field_value')
        widgets = {
            'field_name': forms.TextInput(attrs={'size': 15}),
            'field_value': forms.TextInput(attrs={'size': 15})
            }

# class BaseInvalidCriteriaFormSet(BaseFormSet):
#     def save(self):
#         pass

TaskInvalidCriteriaFormSet = forms.models.modelformset_factory(
                                TaskInvalidationCriterion,
                                form=TaskInvalidationCriterionForm)

class TaskImportBatchForm(forms.ModelForm):
    def save(self, creator, *args, **kwargs):
        self.instance.creator = creator
        super(TaskImportBatchForm, self).save(*args, **kwargs)
        self._process_criteria(creator)
        return self.instance

    def clean(self):
        # TODO mzf: see limit and offset parameters to get first 100 "fresh" bugs (based on query and bug number)
        max_size = 20
        cleaned_data = super(TaskImportBatchForm, self).clean()
        if cleaned_data.get('query','').count('?') != 1:
            raise forms.ValidationError(_('Please provide a full URL as your query.'))
        bugcount = request_bugcount(cleaned_data['query'].split('?')[1])
        if not bugcount:
            raise forms.ValidationError(_('Your query does not return any results.'))
        elif bugcount > max_size:
            raise forms.ValidationError(_(' '.join(['Your query returns more than', str(max_size), 'items.'])))

        return cleaned_data

    def _process_criteria(self, creator):
        pass

    class Meta:
        model = TaskImportBatch
        fields = ('description', 'query')
        widgets = {
            'query': forms.TextInput(attrs={'size': 100}),
            }


class TaskForm(forms.ModelForm):
    keywords = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 50}))

    def __init__(self, *args, **kwargs):
        if kwargs['instance']:
            initial = kwargs.get('initial', {})
            initial['keywords'] = kwargs['instance'].keywords_list
            kwargs['initial'] = initial
        super(TaskForm, self).__init__(*args, **kwargs)
        # self.fields['keywords'].value = self.instance.keywords_list

    def save(self, creator, *args, **kwargs):
        self.instance.creator = creator
        super(TaskForm, self).save(*args, **kwargs)
        self._process_keywords(creator)
        return self.instance

    def _process_keywords(self, creator):
        if 'keywords' in self.changed_data:
            for taskkeyword in self.instance.keyword_set.all():
                taskkeyword.delete()
            for keyword in self.cleaned_data['keywords'].split(','):
                if len(keyword.strip()):
                    self.instance.keyword_set.create(name=keyword.strip(), creator=creator)

    def clean(self):
        cleaned_data = super(TaskForm, self).clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError(_("'End date' must be after 'Start date'"))
        return cleaned_data

    class Meta:
        model = Task
        fields = ('name', 'short_description', 'execution_time', 'difficulty',
                  'repeatable', 'team', 'project', 'type', 'start_date',
                  'end_date', 'why_this_matters', 'prerequisites', 'instructions',
                  'is_draft', 'is_valid')
        widgets = {
            'name': forms.TextInput(attrs={'size': 100}),
            'short_description': forms.TextInput(attrs={'size': 100}),
            'execution_time': HorizRadioSelect,
            'instructions': AceWidget(mode='markdown', theme='textmate', width='800px',
                                      height='300px', wordwrap=True),
            'start_date': CalendarInput,
            'end_date': CalendarInput,
            'why_this_matters': forms.Textarea(attrs={'cols': 100, 'rows': 2}),
            'prerequisites': forms.Textarea(attrs={'cols': 100, 'rows': 4}),
        }

    class Media:
        css = {
            'all': ('css/admin_ace.css',)
        }


class TaskModelForm(forms.ModelForm):
    instructions = forms.CharField(widget=AceWidget(mode='markdown', theme='textmate', width='800px',
                                                    height='600px', wordwrap=True))

    class Meta:
        model = Task

    class Media:
        css = {
            'all': ('css/admin_ace.css',)
        }

    instructions.help_text = ('Instructions are written in <a href="http://markdowntutorial.com/" target="_blank">Markdown</a>.')
