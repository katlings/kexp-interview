import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Comment
from .utils import add_comments_from_db, fetch_plays


log = logging.getLogger(__name__)


def now_playing(request):
    """
    Fetch all the songs played on KEXP in the last 60 minutes and display them
    along with any comments we have about them in our db.
    """
    ## First, fetch all the songs KEXP played in the last hour
    try:
        recent_plays = fetch_plays()
    except Exception as e:
        log.exception('Failed to fetch plays from KEXP API')
        return HttpResponse('Recently played songs could not be fetched', status=400)

    ## Then, grab any already existing comments out of the database

    # It would be conceptually simple to go through each play in the list and
    # check for a comment in the database, but that means we'd do multiple db
    # queries per page load, which is suboptimal in terms of load time. Instead
    # we'll batch the query to grab all relevant comments and sort them out in
    # a helper function.
    recent_plays = add_comments_from_db(recent_plays)

    return render(request,
                  'comment/now_playing.html',
                  {'recent_plays': recent_plays})


def add_comment(request, playid):
    comment, _ = Comment.objects.get_or_create(playid=playid)
    comment.comment = request.POST['comment']
    comment.save()
    return HttpResponseRedirect(reverse('comment:now_playing'))
