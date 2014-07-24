# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from rest_framework import serializers

from oneanddone.tasks.models import Task, TaskKeyword


class TaskKeywordSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskKeyword
        fields = ('name',)


class TaskSerializer(serializers.ModelSerializer):

    project = serializers.SlugRelatedField(many=False, slug_field='name')
    team = serializers.SlugRelatedField(many=False, slug_field='name')
    type = serializers.SlugRelatedField(many=False, slug_field='name')
    keyword_set = TaskKeywordSerializer(required=False, many=True)

    # TODO mzf add new fields like is_valid
    class Meta:
        model = Task
        fields = ('id', 'name', 'short_description', 'instructions',
                  'prerequisites', 'execution_time', 'start_date', 'end_date',
                  'is_draft', 'project', 'team', 'type', 'repeatable', 'difficulty',
                  'why_this_matters', 'keyword_set')
