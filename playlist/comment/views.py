from django.http import HttpResponse
from django.shortcuts import render

from .models import Comment
from .utils import fetch_songs


def now_playing(request):
    ## First, fetch all the songs KEXP played in the last hour
    try:
        recently_played = fetch_songs()
    except Exception as e:
        # log e
        return HttpResponse('Recently played songs could not be fetched', status=400)

    ## Then, grab any already existing comments out of the database
    # fetch comments from db in a batch for fewer queries
    recently_played_ids = [song.playid for song in recently_played]
    # stick them in a dictionary for easier matching to the songs we've grabbed
    comments = {c.playid: c for c in Comment.objects.filter(playid__in=recently_played_ids)}

    for song in recently_played:
        if song.playid in comments:
            song.comment = comments[song.playid]

    return HttpResponse(recently_played)
