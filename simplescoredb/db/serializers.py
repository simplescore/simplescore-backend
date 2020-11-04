from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from rest_framework import serializers
from simplescoredb.db.models import Song, Chart, Score, PartialScore, SHA3SumField

from simplescoredb.db import ksh
from .validators import SHA3SumValidator

import dataclasses

class SHA3SumField(serializers.CharField):
    validators = [SHA3SumValidator]

    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        super().__init__(**kwargs)

class SongSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Song
        fields = ['url', 'id', 'title', 'artist', 'chart_set']
        read_only_fields = ['chart_set']

class ChartSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Chart
        fields = ['url', 'id', 'sha3', 'song', 'charter', 'difficulty_index', 'difficulty_shortname', 'difficulty_name', 'score_set']
        read_only_fields = ['sha3', 'score_set']

class ScoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Score
        fields = ['url', 'id', 'player', 'chart', 'display_score', 'judgements', 'max_chain', 'gauge', 'submission_time']
        read_only_fields = ['submission_time']

class ScoreSubmissionSerializer(serializers.HyperlinkedModelSerializer):
    player = serializers.HiddenField(default=None)

    class Meta:
        model = PartialScore
        fields = ['url', 'player', 'chart_sha3', 'display_score', 'judgements', 'max_chain', 'gauge', 'submission_time']
        read_only_fields = ['submission_time']

class ChartFileSubmissionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    contents = serializers.CharField(max_length=1024 * 1024 * 5)

class SongChartSubmissionSerializer(serializers.Serializer):
    class ChartPartialSerializer(ChartSerializer):
        class Meta:
            model = Chart
            fields = [f.name for f in dataclasses.fields(ksh.ChartData)]

    class SongPartialSerializer(SongSerializer):
        class Meta:
            model = Song
            fields = [f.name for f in dataclasses.fields(ksh.SongData)]

    sha3 = serializers.CharField(max_length=128)
    chart = ChartPartialSerializer()
    song = SongPartialSerializer()

    class Meta:
        fields = ['url', 'sha3', 'chart', 'song']

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'password']
        read_only_fields = ['password']
