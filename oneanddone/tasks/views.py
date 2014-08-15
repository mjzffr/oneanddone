# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib import messages
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import get_template
from django.views import generic

from braces.views import LoginRequiredMixin
from datetime import date, timedelta
from django_filters.views import FilterView
from rest_framework import generics
from tower import ugettext as _

from oneanddone.base.util import get_object_or_none
from oneanddone.tasks.bugzilla import request_bugs
from oneanddone.tasks.filters import TasksFilterSet
from oneanddone.tasks.forms import FeedbackForm, TaskImportBatchForm, TaskInvalidCriteriaFormSet, TaskForm
from oneanddone.tasks.mixins import APIRecordCreatorMixin, APIOnlyCreatorMayDeleteMixin
from oneanddone.tasks.mixins import TaskMustBeAvailableMixin, HideNonRepeatableTaskMixin
from oneanddone.tasks.models import BugzillaBug, Feedback, Task, TaskAttempt, TaskInvalidationCriterion
from oneanddone.tasks.serializers import TaskSerializer
from oneanddone.users.mixins import MyStaffUserRequiredMixin, PrivacyPolicyRequiredMixin


class AvailableTasksView(TaskMustBeAvailableMixin, FilterView):
    queryset = Task.objects.order_by('-execution_time')
    context_object_name = 'tasks'
    template_name = 'tasks/list.html'
    paginate_by = 10
    filterset_class = TasksFilterSet


class RandomTasksView(TaskMustBeAvailableMixin, generic.ListView):
    queryset = Task.objects.order_by('?')
    template_name = 'tasks/random.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(RandomTasksView, self).get_context_data(*args, **kwargs)
        # Only return 5 tasks
        ctx['random_task_list'] = ctx['object_list'][:5]
        return ctx


class TaskDetailView(generic.DetailView):
    model = Task
    template_name = 'tasks/detail.html'
    allow_expired_tasks = True

    def get_context_data(self, *args, **kwargs):
        ctx = super(TaskDetailView, self).get_context_data(*args, **kwargs)
        task = self.object
        if self.request.user.is_authenticated():
            ctx['attempt'] = get_object_or_none(TaskAttempt, user=self.request.user,
                                                task=task, state=TaskAttempt.STARTED)

        # determine label for Get Started button
        if task.is_taken:
            gs_button_label = _('Taken')
            gs_button_disabled = True
        elif task.is_completed:
            gs_button_label = _('Completed')
            gs_button_disabled = True
        else:
            gs_button_label = _('Get Started')
            gs_button_disabled = False
        ctx['gs_button_label'] = gs_button_label
        ctx['gs_button_disabled'] = gs_button_disabled

        return ctx


class StartTaskView(PrivacyPolicyRequiredMixin, HideNonRepeatableTaskMixin,
                    generic.detail.SingleObjectMixin, generic.View):
    model = Task

    def post(self, *args, **kwargs):
        # Do not allow users to take more than one task at a time
        if self.request.user.attempts_in_progress.exists():
            messages.error(self.request, _('You may only work on one task at a time.'))
            return redirect('base.home')

        task = self.get_object()
        if not task.is_available:
            messages.error(self.request, _('That task is unavailable at this time.'))
            return redirect('tasks.available')

        attempt, created = TaskAttempt.objects.get_or_create(user=self.request.user, task=task,
                                                             state=TaskAttempt.STARTED)
        return redirect(task)


class TaskAttemptView(PrivacyPolicyRequiredMixin, generic.detail.SingleObjectMixin, generic.View):
    def get_queryset(self):
        return TaskAttempt.objects.filter(user=self.request.user, state=TaskAttempt.STARTED)


class AbandonTaskView(TaskAttemptView):
    def post(self, *args, **kwargs):
        attempt = self.get_object()
        attempt.state = TaskAttempt.ABANDONED
        attempt.save()

        return redirect('tasks.feedback', attempt.pk)


class FinishTaskView(TaskAttemptView):
    def post(self, *args, **kwargs):
        attempt = self.get_object()
        attempt.state = TaskAttempt.FINISHED
        attempt.save()

        return redirect('tasks.feedback', attempt.pk)


class CreateFeedbackView(PrivacyPolicyRequiredMixin, HideNonRepeatableTaskMixin, generic.CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'tasks/feedback.html'

    def dispatch(self, request, *args, **kwargs):
        self.attempt = get_object_or_404(TaskAttempt, pk=kwargs['pk'], user=request.user,
                                         state__in=[TaskAttempt.FINISHED, TaskAttempt.ABANDONED])
        return super(CreateFeedbackView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super(CreateFeedbackView, self).get_context_data(*args, **kwargs)
        ctx['attempt'] = self.attempt
        return ctx

    def form_valid(self, form):
        feedback = form.save(commit=False)
        feedback.attempt = self.attempt
        feedback.save()

        # Send email to task owner
        task_name = feedback.attempt.task.name
        subject = 'Feedback on %s from One and Done' % task_name
        task_link = 'http'
        if self.request.is_secure():
            task_link += 's'
        task_link += '://%s%s' % (
            self.request.get_host(),
            feedback.attempt.task.get_absolute_url())
        template = get_template('tasks/emails/feedback_email.txt')

        message = template.render({
            'feedback_user': feedback.attempt.user.email,
            'task_name': task_name,
            'task_link': task_link,
            'task_state': feedback.attempt.get_state_display(),
            'feedback': feedback.text})

        # Manually replace quotes and double-quotes as these get
        # escaped by the template and this makes the message look bad.
        filtered_message = message.replace('&#34;', '"').replace('&#39;', "'")

        send_mail(
            subject,
            filtered_message,
            'oneanddone@mozilla.com',
            [feedback.attempt.task.creator.email])

        messages.success(self.request, _('Your feedback has been submitted. Thanks!'))
        return redirect('base.home')


class ListTasksView(LoginRequiredMixin, MyStaffUserRequiredMixin, FilterView):
    queryset = Task.objects.order_by('-modified')
    context_object_name = 'tasks'
    template_name = 'tasks/list.html'
    paginate_by = 20
    filterset_class = TasksFilterSet


import logging
log = logging.getLogger('playdoh')


class ImportTasksView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.TemplateView):

    def get_template_names(self):
        log.debug('Session %r' % self.request.session.get('task_import_data'))
        log.debug('Bugs %r' % self.request.session.get('bugs'))
        log.debug('Stage %r' % self.stage)
        if self.stage == 'preview':
            # After initial form submission
            return ['tasks/confirmation.html']
        else:
            # Initial form load, error or after cancelling from confirmation
            return ['tasks/form.html']

    def get_forms(self, session=False):
        kwargs = {'initial': None}
        if session:
            kwargs['data'] = self.request.session['task_import_data']
        elif self.request.method in ('POST', 'PUT'):
            kwargs['data'] = self.request.POST

        batch_form = TaskImportBatchForm(instance=None,
                                         prefix='batch', **kwargs)
        criterion_formset = TaskInvalidCriteriaFormSet(
            queryset=TaskInvalidationCriterion.objects.none(),
            prefix='criteria',
            **kwargs)
        kwargs['initial'] = {'end_date' : date.today() + timedelta(days=90)}
        task_form = TaskForm(instance=None, prefix='task', **kwargs)

        return {'criterion_formset': criterion_formset,
                'batch_form': batch_form,
                'task_form': task_form}

    def get_context_data(self, **kwargs):
        # Won't have to do this as of Django 1.5
        # https://docs.djangoproject.com/en/1.5/ref/class-based-views/mixins-simple/
        ctx = kwargs
        ctx['action'] = 'Import'
        ctx['cancel_url'] = reverse('tasks.list')
        return ctx

    def forms_valid(self, forms):
        if self.stage == 'confirm':
            return self.done(forms, self.request.session['task_import_bugs'])
        else:
            assert self.stage == 'preview'
            self.request.session['task_import_data'] = self.request.POST
            self.request.session['task_import_bugs'] = bugs = self._get_bugs(forms['batch_form'])
            ctx = forms
            ctx['basename'] = forms['task_form'].cleaned_data['name']
            ctx['bug_ids'] = [bug['id'] for bug in bugs]
            ctx['num_tasks'] = len(bugs)
            ctx['bugzilla_url'] = 'https://bugzilla.mozilla.org/show_bug.cgi?id='
            return self.render_to_response(self.get_context_data(**ctx))

    def forms_invalid(self, forms):
        self.stage = 'error'
        return self.render_to_response(self.get_context_data(**forms))

    def get(self, request, *args, **kwargs):
        # Assume this is a fresh start to the import process
        self.stage = None
        self._reset_session()
        forms = self.get_forms()
        return self.render_to_response(self.get_context_data(**forms))

    def post(self, request, *args, **kwargs):
        stage = self._update_stage()
        if stage == 'initial':
            forms = self.get_forms(session=True)
            return self.render_to_response(self.get_context_data(**forms))
        elif stage == 'preview':
            forms = self.get_forms()
        elif stage == 'confirm':
            forms = self.get_forms(session=True)

        if all([form.is_valid() for form in forms.values()]):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def done(self, forms, bugs):
        self._reset_session()

        import_batch = forms['batch_form'].save(self.request.user)
        criterion_objs = forms['criterion_formset'].save(commit=False)
        for criterion in criterion_objs:
            criterion.batch = import_batch
            criterion.save()

        task = forms['task_form'].save(self.request.user, commit=False)
        keywords = [k.strip() for k in forms['task_form'].cleaned_data['keywords'].split(',')]
        task.batch = import_batch
        basename = task.name
        for bug in bugs:
            bug_obj, _created = BugzillaBug.objects.get_or_create(bugzilla_id=bug['id'])
            bug_obj.summary = bug['summary']
            bug_obj.save()
            task.pk = None
            task.name = ' '.join([basename, 'Bug', str(bug['id'])])
            task.imported_item = bug_obj
            task.save()
            task.replace_keywords(keywords, self.request.user)

        messages.success(self.request, _(' '.join([str(len(bugs)), 'tasks created.'])))
        return redirect('tasks.list')

    def _update_stage(self):
        self.stage = self.request.POST.get('stage')
        if self.stage not in ['initial', 'preview', 'confirm']:
            raise ValidationError(_('Form data is missing or has been tampered.'))
        return self.stage

    def _get_bugs(self, batch_form):
        return request_bugs(batch_form.cleaned_data['query'].split('?')[1])

    def _reset_session(self):
        for name in ['task_import_data', 'task_import_bugs']:
            if self.request.session.get(name):
                del self.request.session[name]

class CreateTaskView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(CreateTaskView, self).get_context_data(*args, **kwargs)
        ctx['task_form'] = ctx.get('form')
        #del ctx['form']
        ctx['action'] = 'Add'
        ctx['cancel_url'] = reverse('tasks.list')
        ctx['ctx'] = ctx
        return ctx

    def form_valid(self, form):
        form.save(self.request.user)

        messages.success(self.request, _('Your task has been created.'))
        return redirect('tasks.list')

# TODO mzf review/fix/add tests

class UpdateTaskView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(UpdateTaskView, self).get_context_data(*args, **kwargs)
        ctx['task_form'] = ctx.get('form')
        #del ctx['form']
        ctx['action'] = 'Update'
        ctx['cancel_url'] = reverse('tasks.detail', args=[self.get_object().id])
        return ctx

    def form_valid(self, form):
        form.save(self.request.user)

        messages.success(self.request, _('Your task has been updated.'))
        return redirect('tasks.list')


class TaskListAPI(APIRecordCreatorMixin, generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskDetailAPI(APIOnlyCreatorMayDeleteMixin,
                    generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
