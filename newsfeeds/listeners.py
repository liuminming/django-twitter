def push_newsfeed_to_cache(sender, instance, created, **kwargs):
    # created is one of the parameters inside kwargs
    # kwargs.get('created')
    if not created:
        return
    from newsfeeds.services import NewsFeedService
    NewsFeedService.push_newsfeed_to_cache(instance)