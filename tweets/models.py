from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User

from likes.models import Like
from utils.time_helpers import utc_now


class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='who posts this tweet',
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    @property
    def comments(self):
        return self.comment_set.all()
        # return Comment.objects.filter(tweet=self)

    @property
    def hours_to_now(self):
        #datetime.now has no time zone info, need to add time zone info of utc
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    def __str__(self):
        # it will print the content when printing
        return f'{self.created_at} {self.user}: {self.content}'
