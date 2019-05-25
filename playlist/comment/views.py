from django.http import HttpResponse
from django.shortcuts import render

from .utils import fetch_songs


def now_playing(request):
    recently_played = fetch_songs()

    for song in recently_played:
        # if song.playid exists in database, get comment
        pass

    # fetch songs from api
    # do not add to database; instead look in database
    return HttpResponse(recently_played)
