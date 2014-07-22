# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils import timezone

import bleach
import jinja2
from markdown import markdown

from oneanddone.base.models import CachedModel, CreatedByModel, CreatedModifiedModel

class TaskInvalidationCriterion(models.Model):
    NOT_EQUAL = 0
    EQUAL = 1
    field_name = models.CharField(max_length=80)
    field_value = models.CharField(max_length=80)
    relation = models.IntegerField(choices=(
                (EQUAL, '=='),
                (NOT_EQUAL, '!=')
               ))
    template = models.ForeignKey('TaskImportBatch')

    def __unicode__(self):
        return ''.join([self.field_name, self.relation, self.field_value])


class TaskImportBatch(CreatedModifiedModel, CreatedByModel):
    name = models.CharField(max_length=255)
    query = models.CharField(max_length=255)
    template = models.ForeignKey('TaskTemplate')

    def __unicode__(self):
        return self.name

    query.help_text = """
        The URL to the search query that yields the items you want to
        create tasks from.
    """


class TaskImportedInfo(models.Model):
    # other sources might be Moztrap, etc.
    BUGZILLA = 0
    OTHER = 1
    source = models.IntegerField(
        choices=(
            (BUGZILLA, 'Bugzilla@Mozilla'),
            (OTHER, 'Other')
        ),
        default=BUGZILLA)


class BugzillaBug(TaskImportedInfo):
    summary = models.CharField(max_length=255)
    bugzilla_id = models.IntegerField(max_length=20, unique=True)

    def __unicode__(self):
        return ' '.join(['Bug', self.bugzilla_id])


class TaskProject(CachedModel, CreatedModifiedModel, CreatedByModel):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class TaskTeam(CachedModel, CreatedModifiedModel, CreatedByModel):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class TaskType(CachedModel, CreatedModifiedModel, CreatedByModel):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class TaskTemplate(CachedModel, CreatedModifiedModel, CreatedByModel):
    """Task that is used as a base with a TaskImportBatch"""
    project = models.ForeignKey(TaskProject, blank=True, null=True)
    team = models.ForeignKey(TaskTeam)
    type = models.ForeignKey(TaskType, blank=True, null=True)

    EASY = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    difficulty = models.IntegerField(
        choices=(
            (EASY, 'Easy'),
            (INTERMEDIATE, 'Intermediate'),
            (ADVANCED, 'Advanced')
        ),
        default=EASY,
        verbose_name='task difficulty')
    execution_time = models.IntegerField(
        choices=((i, i) for i in (15, 30, 45, 60)),
        blank=False,
        default=15,
        verbose_name='estimated time'
    )
    instructions = models.TextField()
    is_draft = models.BooleanField(verbose_name='draft?')
    is_valid = models.BooleanField(verbose_name='valid?', default=True)
    name = models.CharField(max_length=255, verbose_name='title')
    prerequisites = models.TextField(blank=True)
    repeatable = models.BooleanField(default=True)
    short_description = models.CharField(max_length=255, verbose_name='description')
    why_this_matters = models.TextField(blank=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    def _yield_html(self, field):
        """
        Return the requested field for a task after parsing them as
        markdown and bleaching/linkifying them.
        """
        linkified_field = bleach.linkify(field, parse_email=True)
        html = markdown(linkified_field, output_format='html5')
        cleaned_html = bleach.clean(html, tags=settings.INSTRUCTIONS_ALLOWED_TAGS,
                                    attributes=settings.INSTRUCTIONS_ALLOWED_ATTRIBUTES)
        return jinja2.Markup(cleaned_html)

    @property
    def instructions_html(self):
        return self._yield_html(self.instructions)

    @property
    def prerequisites_html(self):
        return self._yield_html(self.prerequisites)

    @property
    def why_this_matters_html(self):
        return self._yield_html(self.why_this_matters)

    def get_absolute_url(self):
        return reverse('tasks.detail', args=[self.id])

    def get_edit_url(self):
        return reverse('tasks.edit', args=[self.id])

    def __unicode__(self):
        return self.name

    # Help text
    instructions.help_text = """
        Markdown formatting is applied. See
        <a href="http://www.markdowntutorial.com/">http://www.markdowntutorial.com/</a> for a
        primer on Markdown syntax.
    """
    execution_time.help_text = """
        How many minutes will this take to finish?
    """
    start_date.help_text = """
        Date the task will start to be available. Task is immediately available if blank.
    """
    end_date.help_text = """
        If a task expires, it will not be shown to users regardless of whether it has been
        finished.
    """
    is_draft.help_text = """
        If you do not wish to publish the task yet, set it as a draft. Draft tasks will not
        be viewable by contributors.
    """


class Task(TaskTemplate):
    """
    Task for a user to attempt to fulfill.
    """
    external_item = models.ForeignKey(TaskImportedInfo, blank=True, null=True)
    batch = models.ForeignKey(TaskImportBatch, blank=True, null=True)
    # We set parent_link=True to control the name of the generated column,
    # which eases data migration
    task_template = models.OneToOneField(TaskTemplate, parent_link=True)

    @property
    def is_available(self):
        """Whether this task is available for users to attempt."""
        if self.is_draft:
            return False

        now = timezone.now()
        return not (
            (self.end_date and now > self.end_date) or
            (self.start_date and now < self.start_date)
        )

    def is_available_to_user(self, user):
        repeatable_filter = Q(~Q(user=user) & ~Q(state=TaskAttempt.ABANDONED))
        return self.is_available and (
            self.repeatable or not self.taskattempt_set.filter(repeatable_filter).exists())

    @property
    def keywords_list(self):
        return ', '.join([keyword.name for keyword in self.keyword_set.all()])

    @property
    def is_taken(self):
        return not self.repeatable and self.taskattempt_set.filter(state=TaskAttempt.STARTED).exists()

    @property
    def is_completed(self):
        return not self.repeatable and self.taskattempt_set.filter(state=TaskAttempt.FINISHED).exists()

    @classmethod
    def is_available_filter(self, now=None, allow_expired=False, prefix=''):
        """
        Return a Q object (queryset filter) that matches available
        tasks.

        :param now:
            Datetime to use as the current datetime. Defaults to
            django.utils.timezone.now().

        :param allow_expired:
            If False, exclude tasks past their end date.

        :param prefix:
            Prefix to use for queryset filter names. Good for when you
            want to filter on a related tasks and need 'task__'
            prepended to the filters.
        """
        # Convenient shorthand for creating a Q filter with the prefix.
        pQ = lambda **kwargs: Q(**dict((prefix + key, value) for key, value in kwargs.items()))

        now = now or timezone.now()
        now = now.replace(hour=0, minute=0, second=0)  # Use just the date to allow caching
        q_filter = pQ(is_draft=False) & (pQ(start_date__isnull=True) | pQ(start_date__lte=now))

        if not allow_expired:
            q_filter = q_filter & (pQ(end_date__isnull=True) | pQ(end_date__gt=now))

        q_filter = q_filter & (
            pQ(repeatable=True) | (
                ~pQ(taskattempt__state=TaskAttempt.STARTED) &
                ~pQ(taskattempt__state=TaskAttempt.FINISHED)))

        return q_filter


class TaskKeyword(CachedModel, CreatedModifiedModel, CreatedByModel):
    task_template = models.ForeignKey(TaskTemplate, related_name='keyword_set')
    name = models.CharField(max_length=255, verbose_name='keyword')

    def __unicode__(self):
        return self.name


class TaskAttempt(CachedModel, CreatedModifiedModel):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    task = models.ForeignKey(Task)

    STARTED = 0
    FINISHED = 1
    ABANDONED = 2
    state = models.IntegerField(default=STARTED, choices=(
        (STARTED, 'Started'),
        (FINISHED, 'Finished'),
        (ABANDONED, 'Abandoned')
    ))

    def __unicode__(self):
        return u'{user} attempt [{task}]'.format(user=self.user, task=self.task)

    class Meta(CreatedModifiedModel.Meta):
        ordering = ['-modified']


class Feedback(CachedModel, CreatedModifiedModel):
    attempt = models.ForeignKey(TaskAttempt)
    text = models.TextField()

    def __unicode__(self):
        return u'Feedback: {user} for {task}'.format(
            user=self.attempt.user, task=self.attempt.task)
