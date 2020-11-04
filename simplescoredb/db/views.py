from django.shortcuts import render
from django.core import exceptions
from django.forms.models import model_to_dict
from rest_framework import views, status, generics, viewsets, serializers, permissions
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User

from simplescoredb.db.models import Song, Chart, Score, PartialScore
from simplescoredb.db.serializers import SongSerializer, ChartSerializer, ScoreSerializer, SongChartSubmissionSerializer, ChartFileSubmissionSerializer, UserSerializer, ScoreSubmissionSerializer

from simplescoredb.db import ksh

RESPONSE_KEY_DETAIL = 'detail'

# Create your views here.
class SongViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

class ChartViewSet(viewsets.ModelViewSet):
    queryset = Chart.objects.all()

    def get_permissions(self):
        # Respects the permissions provided via function annotation.
        if self.action is not None and hasattr(getattr(self, self.action), 'permission_classes'):
            permission_classes = getattr(self, self.action).permission_classes
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create_with_song':
            return DetailedChartSerializer
        else:
            return ChartSerializer

    @action(detail=False, url_path='sha3/(?P<sha3sum>[a-z0-9]+)')
    def get_by_sha3(self, request, sha3sum):
        """
        Find a chart given its checksum.
        """
        try:
            chart = Chart.objects.get(sha3=sha3sum)
            return Response(ChartSerializer(chart).data)
        except exceptions.ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """
        Submit a chart by uploading the contents of a chart file.
        Creates a new song if necessary.
        """
        serialized = ChartFileSubmissionSerializer(data=request.data)
        if not serialized.is_valid():
            print(serialized.errors)
            return Response({RESPONSE_KEY_DETAIL: serialized.errors['contents']}, status=status.HTTP_400_BAD_REQUEST)
        sha3, chart_data, song_data = ksh.load_ksh(serialized.data)
        return self._create_with_song(sha3, vars(chart_data), vars(song_data))

    @action(detail=False, url_path='submit-meta', methods=['post'])
    @permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
    def submit_metadata(self, request):
        """ 
        Submit a song by giving metadata about the song and chart.
        Creates a new song if necessary.
        This is meant for debug purposes only; normal clients should submit the chart file itself.
        """
        return self._create_with_song(request.data.get('sha3'), request.data.get('song'), request.data.get('chart'))
    
    def _create_with_song(self, sha3, song, chart):
        if Chart.objects.filter(sha3=sha3).exists():
            return Response({RESPONSE_KEY_DETAIL: 'chart with that sha3 already exists' },
                    status=status.HTTP_400_BAD_REQUEST)

        print(f'CREATE CHART\n{sha3}\n{song}\n{chart}')

        submission_data = { 'sha3': sha3, 'song': song, 'chart': chart }
        serialized = SongChartSubmissionSerializer(data=submission_data)
        if serialized.is_valid():
            created_song = False

            # Serialize song metadata.
            song_serialized = SongChartSubmissionSerializer.SongPartialSerializer(data=song)
            if not song_serialized.is_valid():
                raise exceptions.ValidationError(song_serialized.errors)
            
            db_song = None
            try:
                db_song = Song.objects.get(**song_serialized.data)
            except exceptions.ObjectDoesNotExist:
                created_song = True
                db_song = Song(**song_serialized.data)
                db_song.save()

            chart_serialized = SongChartSubmissionSerializer.ChartPartialSerializer(data=chart)
            if not chart_serialized.is_valid():
                if created_song is True:
                    db_song.delete()
                raise exceptions.ValidationError(chart_serialized.errors)
            db_chart = Chart(sha3=sha3, **chart_serialized.data)
            db_chart.song = db_song
            db_chart.save()

            return Response({ 'did_create_song': created_song })
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ScoreSubmissionSerializer
        else:
            return ScoreSerializer

    def create(self, request):
        serialized = ScoreSubmissionSerializer(data=request.data, context={'request': request})
        if not serialized.is_valid():
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

        score = serialized.validated_data
        
        chart = None
        db_score = None
        try:
            chart = Chart.objects.get(sha3=score.get('chart_sha3'))
            # Create score with all the data except the chart checksum; instead pass the chart reference itself.
            db_score = Score(**{ k: score[k] for k in score.keys() - ['chart_sha3', 'player']}, chart=chart, player=request.user)
        except exceptions.ObjectDoesNotExist:
            db_score = PartialScore(**{ k: score[k] for k in score.keys() - ['player']}, player=request.user)

        db_score.save()

        response_data = {
            'score_type': 'partial' if chart is None else 'full',
            **model_to_dict(db_score)
        }

        return Response(response_data)

class PartialScoreViewSet(viewsets.ModelViewSet):
    queryset = PartialScore.objects.all()
    serializer_class = ScoreSubmissionSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    class _Serializer(UserSerializer):
        class Meta(UserSerializer.Meta):
            fields = ['url', 'username']

    queryset = User.objects.all()
    serializer_class = _Serializer
    permission_classes = [permissions.IsAuthenticated]

class RegisterView(views.APIView):
    serializer_class = UserSerializer

    def post(self, request):
        user = User.objects.create_user(request.data.get('username'), password=request.data.get('password'))
        return Response()
