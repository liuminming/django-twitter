from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User


class Like(models.Model):
    # user liked content_object at created_at
    content_object = GenericForeignKey('content_type', 'object_id')
    # # https://docs.djangoproject.com/en/3.1/ref/contrib/contenttypes/#generic-relations
    object_id = models.PositiveIntegerField() # comment id or tweet id
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        # 这里使用 unique together 也就会建一个 <user, content_type, object_id>
        # 的索引。这个索引同时还可以具备查询某个 user like 了哪些不同的 objects 的功能
        # 因此如果 unique together 改成 <content_type, object_id, user>
        # 就没有这样的效果了
        unique_together = (('user', 'content_type', 'object_id'),)

        index_together = (
            # fetch all the likes of a certain object
            ('content_type', 'object_id', 'created_at'),
            # fetch all objects liked by a user
            ('user', 'content_type', 'created_at')
        )

    def __str__(self):
        return '{} - {} liked {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id
        )