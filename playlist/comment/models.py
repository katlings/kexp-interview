from django.db import models


class Comment(models.Model):
    """
    We're going minimal here: only store the comment data with a pointer
    to the external API. This saves space and doesn't duplicate much work,
    since we'll need to check the API upon every page load anyway.
    """
    playid = models.IntegerField()
    comment = models.CharField(max_length=2048)

    def __str__(self):
        return f'{self.comment}'
