import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Comment
from .utils import fetch_play, fetch_plays


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

    # it would be conceptually simpler to go through each play in the list and
    # check for a comment, but that means we'd do multiple db queries per page
    # load, which is suboptimal in terms of load time. instead we'll batch the
    # query to grab all relevant comments and sort them out later.
    recent_play_ids = [play.playid for play in recent_plays]
    # stick them in a dictionary for easier matching to the plays we've grabbed
    comments = {c.playid: c for c in Comment.objects.filter(playid__in=recent_play_ids)}

    for play in recent_plays:
        if play.playid in comments:
            play.comment = comments[play.playid]

    return render(request,
                  'comment/now_playing.html',
                  {'recent_plays': recent_plays})


def add_comment(request, playid):
    comment, _ = Comment.objects.get_or_create(playid=playid)
    comment.comment = request.POST['comment']
    comment.save()
    return HttpResponseRedirect(reverse('comment:now_playing'))


def last_commented(request):
    """
    Fetch the last 20 comments added to plays and display them alongside song
    data. This is mostly for testing (since comments on the main page
    essentially expire after an hour).
    """
    comments = Comment.objects.all()
    plays = []

    for comment in comments[:20]:
        play = fetch_play(comment.playid)

        if play is None:
            # log an error
            continue

        play.comment = comment.comment
        plays.append(play)

    return HttpResponse(plays)
