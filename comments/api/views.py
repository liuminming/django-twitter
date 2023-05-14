from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from comments.api.permissions import IsObjectOwner
from comments.api.serializers import CommentSerializerForCreate, CommentSerializer, CommentSerializerForUpdate
from comments.models import Comment
from inbox.services import NotificationService
from utils.decorators import required_params


class CommentViewSet(viewsets.GenericViewSet):

    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id', )

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):
         queryset = self.get_queryset()
         # comments = self.filter_queryset(queryset).order_by('created_at')
         # optimize performance
         comments = self.filter_queryset(queryset).prefetch_related('user').order_by('created_at')
         serializer = CommentSerializer(
             comments,
             context = {'request':request},
             many=True,
         )
         return Response({'comments': serializer.data}, status=status.HTTP_200_OK)


    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }

        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        comment = serializer.save()
        NotificationService.send_comment_notification(comment)
        return Response(
            CommentSerializer(comment, context = {'request':request},).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        #get_object uses queryset to filter out the object with the id from url
        serializer = CommentSerializerForUpdate(
            instance = self.get_object(),
            data = request.data,
        )

        if not serializer.is_valid():
            return Response({
                'message':'Please check input',
                'errors':serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context = {'request':request},).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # by default, DRF return 204 no content
        return Response({'success': True}, status=status.HTTP_200_OK)