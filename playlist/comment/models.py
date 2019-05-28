from django.db import models


class Comment(models.Model):
    """
    We're going minimal here: only store the comment data with an id that acts
    as a pointer to the external API. This saves space on our end and doesn't
    require us to duplicate much work in order to get song data to display,
    since we'll be making an API call upon every page load anyway to see if the
    recently played songs have changed.
    """
    # We're going to associate comments with a particular instance of a DJ
    # playing a song; this makes sense because comments could be time-sensitive
    # (e.g. 'This band is coming to Seattle tomorrow'). It's out of scope for
    # this interview project, but it would be cool to store the trackid (and/or
    # artistid!) to save someone some work by pre-populating previous comments
    # left on the same song or other songs by the same artist.
    playid = models.IntegerField(unique=True)
    comment = models.CharField(max_length=2048)

    def __str__(self):
        return self.comment
