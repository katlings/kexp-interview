import datetime
import requests


KEXP_API = 'https://legacy-api.kexp.org/play/'


class Play:
    """
    A simplified representation of a song play on KEXP
    """
    def __init__(self, playid, title, artist, album, airdatestr):
        self.playid = playid
        self.title = title
        self.artist = artist
        self.album = album
        self.airdate = datetime.datetime.strptime(airdatestr, '%Y-%m-%dT%H:%M:%SZ')
        self.comment = None

    @classmethod
    def from_api(cls, playdict):
        """
        Create a Play object directly from the format returned by the KEXP
        API
        """
        if not playdict['playtype']['playtypeid'] == 1:
            return None

        return cls(playdict['playid'],
                   playdict['track']['name'],
                   playdict['artist']['name'],
                   playdict['release']['name'],
                   playdict['airdate'])
    
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
        return self.title == other.title and self.artist == other.artist and self.album == other.album


def fetch_plays(window=3600, end_time=None):
    """
    Fetch the songs that were played on KEXP in the [window] seconds before
    [end_time]. end_time is a timezone-naive datetime object expressing the
    time in UTC, and defaults to the current time.
    
    Return a simplified, easy-to-display format as a list of Play objects
    """

    def is_song_play(playdict):
        # not every entry in the playlist is a song; some are e.g. air breaks
        return playdict.get('playtype', {}).get('playtypeid') == 1

    if end_time is None:
        end_time = datetime.datetime.utcnow()
    begin_time = end_time - datetime.timedelta(seconds=window)

    plays = []

    response = requests.get(KEXP_API, {'begin_time': begin_time, 'end_time': end_time}).json()
    while response.get('results'):
        plays.extend(Play.from_api(result) for result in response['results'] if is_song_play(result))
        response = requests.get(response['next']).json()  # this will throw KeyError if api response is malformed, but it looks like it always provides a next parameter even if the current response is empty

    # sometimes a song will be reported twice from the API with two different
    # playids; it looks like this occurs when a comment is added to the play on
    # the KEXP side (not via this webapp ;) )
    # to avoid double-listing songs when this happens, we're going to look through
    # the list and only keep the lowest playid out of any duplicates.

    # first, make sure we're sorted ascending by playid. NB this puts the most
    # recently played song at the end.
    plays.sort(key=lambda play: play.playid)
    unique_plays = []

    for play in plays:
        # if it's not already in the unique list, add it
        # this isn't the most efficient algorithm (O(n^2)), but it's
        # conceptually simple and we're only dealing with ~20 plays in any
        # given hour so it's still a trivial amount of work
        if not any(play.duplicate(other) for other in unique_plays):
            unique_plays.append(play)

    return unique_plays


def fetch_play(playid):
    response = requests.get(KEXP_API, {'playid': playid}).json()

    if not response.get('results'):
        return None

    return Play.from_api(response['results'][0])
