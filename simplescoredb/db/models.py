from django.db import models
from django.db.models.signals import post_delete
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.contrib.auth.models import User

from .validators import SHA3SUM_LENGTH, SHA3SumValidator

class SHA3SumField(models.CharField):
    def __init__(self):
        super().__init__(max_length=SHA3SUM_LENGTH)
        validators = [SHA3SumValidator]

class Song(models.Model):
    title = models.CharField(max_length=100, db_column='song_title')
    artist = models.CharField(max_length=100, db_column='song_artist')

    class Meta:
        app_label = 'db'

    def __str__(self):
        return f'Song: {self.artist[:8]} – {self.title[:8]}'

class Chart(models.Model):
    class Meta:
        app_label = 'db'

    sha3 = SHA3SumField()
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    charter = models.CharField(max_length=100)
    difficulty_index = models.PositiveSmallIntegerField()
    difficulty_shortname = models.CharField(max_length=8)
    difficulty_name = models.CharField(max_length=50)

    @property
    def metadata_clashes(self):
        return self.__class__.objects.filter(
                song=self.song, charter=self.charter, difficulty_index=self.difficulty_index,
                difficulty_shortname=self.difficulty_shortname, difficulty_name=self.difficulty_name)

    def clean(self):
        difficulty_shortname = difficulty_shortname.upper()

    @staticmethod
    @receiver(post_delete, sender='db.Chart')
    def post_delete(sender, **kwargs):
        # Delete the song if there are no charts remaining for it.
        instance = kwargs['instance']
        if len(instance.song.chart_set.all()) == 0:
            instance.song.delete()

class AbstractScore(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    display_score = models.PositiveIntegerField()
    judgements = models.JSONField()
    max_chain = models.PositiveIntegerField()
    gauge = models.PositiveIntegerField()
    submission_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'db'
        abstract = True

class Score(AbstractScore):
    chart = models.ForeignKey(Chart, on_delete=models.CASCADE)

class PartialScore(AbstractScore):
    """
    A score that has been submitted for a chart with a checksum that doesn't exist yet.
    """
    chart_sha3 = SHA3SumField()
