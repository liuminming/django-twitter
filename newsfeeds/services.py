from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        followers = FriendshipService.get_followers(tweet.user)
        # for + query should not be used in production env
        # 不可以将数据库操作放在 for 循环里， 效率会非常低
        # for follower in followers:
        #     NewsFeed.objects.create(
        #         user=follower,
        #         tweet=tweet,
        #     )
        #should use bulk_create, which will use one insert statement
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)
