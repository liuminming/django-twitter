def incr_likes_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        return

    # 不可以使用
    # tweet = instance.content_object
    # tweet.likes_count += 1
    # tweet.save()
    # 因为这个操作不是原子操作， 必须使用 update 语句才是原子操作
    # SQL Query：UPDATE likes_count = likes_count + 1 FROM tweets_table WHERE id=<instance.object_id>
    # mysql provides row lock, 锁保证线性执行
    # 方法 1
    Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') + 1)

    # 方法 2
    # tweet = instance.content_object
    # tweet.likes_count = F('likes_count') + 1
    # tweet.save()

def decr_likes_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        return

    # handle tweet likes cancel
    tweet = instance.content_object
    Tweet.objects.filter(id=tweet.id).update(likes_count=F('likes_count') - 1)