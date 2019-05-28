from django.db import models


class Comment(models.Model):
    """
    We're going minimal here: only store the comment data with an id that acts
    as a pointer to the external API. This saves space and doesn't duplicate
    much work, since we'll need to make an API call upon every page load anyway
    to see if the recently played songs have changed.
    """
    # We're going to associate comments with a particular instance of playing a
    # song; this makes sense because comments could be time-sensitive (e.g.
    # 'This band is coming to Seattle soon'). If it becomes relevant, we could
    # also store the trackid (or artistid!) and save someone some work by
    # pre-populating previous comments left on the same song or other songs by
    # the artist.
    playid = models.IntegerField()
    comment = models.CharField(max_length=2048)

    def __str__(self):
        return self.comment
