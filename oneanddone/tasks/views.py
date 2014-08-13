# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib import messages
from django.contrib.formtools.utils import form_hmac
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import get_template
from django.views import generic

from braces.views import LoginRequiredMixin
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


# class TestMajaView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.TemplateView):
#     template_name = 'tasks/majatest.html'

#     def get_context_data(self, *args, **kwargs):
#         ctx = super(TestMajaView, self).get_context_data(**kwargs)
#         ctx['test'] = self.template_name
#         ctx['action'] = 'Import'
#         return ctx

# class ConfirmImportView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.edit.ProcessFormView, generic.TemplateView):
#     template_name = 'tasks/confirmation.html'

#     def get_context_data(self, **kwargs):
#         ctx = kwargs
#         ctx['num'] = 2
#         ctx['action'] = 'Import'
#         ctx['cancel_url'] = reverse('tasks.list')
#         return ctx

#     def get(self, request, *args, **kwargs):
#         return self.render_to_response(self.get_context_data(**kwargs))

#     def post(self, request, *args, **kwargs):
#         pass

class ImportTasksView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.TemplateView):

    def get_template_names(self):
        # After initial form submission
        if self.stage == 'preview':
            return ['tasks/confirmation.html']
        else:
        # Initial form load, or after cancelling in response to form preview
            return ['tasks/form.html']

    def dispatch(self, request, *args, **kwargs):
        self.stage = request.POST.get('stage')
        return super(ImportTasksView, self).dispatch(request, *args, **kwargs)

    def get_forms(self):
        kwargs = {'initial': None}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        criterion_formset = TaskInvalidCriteriaFormSet(
            queryset=TaskInvalidationCriterion.objects.none(),
            prefix='criteria', **kwargs)
        batch_form = TaskImportBatchForm(instance=None,
                                         prefix='batch', **kwargs)
        task_form = TaskForm(instance=None, prefix='task', **kwargs)
        return {'criterion_formset': criterion_formset,
                'batch_form': batch_form,
                'task_form': task_form}

    def get_context_data(self, **kwargs):
        # Won't have to do this as of Django 1.5
        # https://docs.djangoproject.com/en/1.5/ref/class-based-views/mixins-simple/
        ctx = kwargs
        ctx['import_obj'] = 'task batch'
        ctx['action'] = 'Import'
        ctx['cancel_url'] = reverse('tasks.list')
        return ctx

    def forms_valid(self, forms):
        if self.stage == 'confirm':
            if self._check_security_hash(self.request.POST.get('hashes'), forms):
                return self.done(forms)
            else:
                return self.failed_hash(request)
        else:
            ctx = forms
            if self.stage == 'preview':
                ctx['hashes'] = self.security_hashes(forms)
                bugs = request_bugs(forms['batch_form'].cleaned_data['query'].split('?')[1])
                basename = forms['task_form'].cleaned_data['name']
                ctx['task_names'] = [' '.join([basename, 'Bug', str(bug['id'])]) for bug in bugs]
                ctx['num_tasks'] = len(bugs)
            return self.render_to_response(self.get_context_data(**ctx))

    def forms_invalid(self, forms):
        return self.render_to_response(self.get_context_data(**forms))

    def get(self, request, *args, **kwargs):
        forms = self.get_forms()
        return self.render_to_response(self.get_context_data(**forms))

    def post(self, request, *args, **kwargs):
        forms = self.get_forms()
        if all([form.is_valid() for form in forms.values()]):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def done(self, forms):
        bugs = request_bugs(forms['batch_form'].cleaned_data['query'].split('?')[1])
        import_batch = forms['batch_form'].save(self.request.user)
        criterion_objs = forms['criterion_formset'].save(commit=False)
        for criterion in criterion_objs:
            criterion.batch = import_batch
            criterion.save()
        task = forms['task_form'].save(self.request.user, commit=False)
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

        messages.success(self.request, _(' '.join([str(len(bugs)), 'tasks created.'])))
        return redirect('tasks.list')

    def security_hashes(self, forms):
        all_forms = [forms['batch_form'], forms['task_form']] + forms['criterion_formset'].forms
        return [form_hmac(form) for form in all_forms]

    def failed_hash(self, request):
        "Returns an HttpResponse in the case of an invalid security hash."
        self.stage = 'preview'
        return self.post(request)

    def _check_security_hash(self, tokens, forms):
        expected = self.security_hashes(forms)
        #none
        if len(tokens) != len(expected):
            return False
        else:
            return all([constant_time_compare(t, e) in zip(tokens, expected)])

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
