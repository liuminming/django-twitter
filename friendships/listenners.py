def invalidate_following_cache(sender, instance, **kwargs):
    # if putting import on top lines, it will cause reference cycle
    from friendships.services import FriendshipService
    FriendshipService.invalidate_following_cache(instance.from_user_id)