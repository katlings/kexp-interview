import datetime
import logging
import pytz
import requests

from .models import Comment


log = logging.getLogger(__name__)
KEXP_API = 'https://legacy-api.kexp.org/play/'


class Play:
    """
    A simplified representation of a song play on KEXP, containing all the data
    necessary to display and store it
    """
    def __init__(self, playid, title, artist, album, airdatestr):
        self.playid = playid
        self.title = title
        self.artist = artist
        self.album = album
        self.airdate = datetime.datetime.strptime(airdatestr, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.UTC)
        self.comment = None

    @classmethod
    def from_api(cls, playdict):
        """
        Create a Play object directly from the format returned by the KEXP
        API
        """
        def get_from_api_dict(key1, key2='name'):
            """
            Sometimes a play won't have e.g. a release/album associated with
            it; we want to be able to safely get the value out if it exists, or
            return None if it doesn't. We can't do this directly with get
            because the key exists and its value is None.
            """
            if playdict.get(key1) is not None:
                return playdict.get(key1).get(key2)
            else:
                return None

        if not get_from_api_dict('playtype', 'playtypeid') == 1:
            return None

        return cls(playdict.get('playid'),
                   get_from_api_dict('track'),
                   get_from_api_dict('artist'),
                   get_from_api_dict('release'),
                   playdict.get('airdate'))
    
    def __repr__(self):
        s = f'{self.title} by {self.artist} from {self.album}'
        if self.comment is not None:
            s = s + f'; {self.comment}'
        return s

    def duplicate(self, other):
        """
        Detect when two plays are of the same song, even if they don't have the
        same playid
        """
        return (self.title == other.title and
                self.artist == other.artist and
                self.album == other.album)


def fetch_plays_from_api(begin_time, end_time):
    """
    The heavy lifting; actually call the KEXP API for recent plays between
    [begin_time] and [end_time] (both timezone-naive datetime objects in UTC)
    and parse the response into simplified Play objects
    """
    def is_song_play(playdict):
        # not every entry in the playlist is a song; some are e.g. air breaks
        return playdict.get('playtype', {}).get('playtypeid') == 1

    plays = []

    response = requests.get(KEXP_API, {'begin_time': begin_time, 'end_time': end_time}).json()
    while response.get('results'):
        plays.extend(Play.from_api(result) for result in response['results'] if result is not None and is_song_play(result))
        # this will throw KeyError if api response is malformed, but it looks
        # like it always provides a next parameter even if the current
        # response is empty
        response = requests.get(response['next']).json()

    return plays


def fetch_plays(window=3600, end_time=None):
    """
    Fetch the songs that were played on KEXP in the [window] seconds before
    [end_time]. end_time is a timezone-naive datetime object expressing the
    time in UTC, and defaults to the current time.

    Return a simplified, easy-to-display format as a list of Play objects
    """

    if end_time is None:
        end_time = datetime.datetime.utcnow()
    begin_time = end_time - datetime.timedelta(seconds=window)

    plays = fetch_plays_from_api(begin_time, end_time)

    # sometimes a song will be reported twice from the API with two different
    # playids; it looks like this can occur when a comment is added to the play
    # on the KEXP side (not via this webapp ;) )
    # to avoid double-listing songs when this happens, we're going to look through
    # the list and only keep the lowest playid out of any duplicates.

    # first, make sure we're sorted ascending by playid. NB this puts the most
    # recently played song at the end.
    plays.sort(key=lambda play: play.playid)
    unique_plays = []

    for play in plays:
        # if it's not already in the unique list, add it
        # this isn't the most efficient algorithm (it's O(n^2)), but it's
        # conceptually simple and we're only dealing with ~20 plays in any
        # given hour so it's still a trivial amount of work
        if not any(play.duplicate(other) for other in unique_plays):
            unique_plays.append(play)

    # it's more intuitive to display the most recently played song first, so
    # reverse the order
    unique_plays.reverse()

    return unique_plays


def add_comments_from_db(plays):
    """
    Fetch comments in one batch from the database for a given set of Play objects,
    and add them to the Play objects.
    NOTE: This modifies the original objects in the plays list. We return the
    list at the end for flexibility, but the list is modified over the course of
    the function; side effects are happening!
    """
    play_ids = [play.playid for play in plays]
    # Fetch comments from db and stick them in a dictionary for easier matching
    # to the relevant set of plays
    comments = {c.playid: c for c in Comment.objects.filter(playid__in=play_ids)}

    for play in plays:
        if play.playid in comments:
            play.comment = comments[play.playid].comment
        else:
            play.comment = None

    return plays
