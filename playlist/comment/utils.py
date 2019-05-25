import datetime
import requests


KEXP_API = 'https://legacy-api.kexp.org/play/'


class Play:
    def __init__(self, playid, title, artist, album):
        self.playid = playid
        self.title = title
        self.artist = artist
        self.album = album
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
                   playdict['release']['name'])
    
    def __repr__(self):
        s = f'{self.title} by {self.artist} from {self.album}'
        if self.comment is not None:
            s = s + f'; {self.comment}'
        return s


def fetch_plays(window=3600):
    """
    Fetch the songs that were played on KEXP in the last [window] seconds
    
    Return in a simplified, easy-to-display format as a list of Play objects
    """

    def is_song_play(playdict):
        # not every entry in the playlist is a song; some are e.g. air breaks
        return playdict.get('playtype', {}).get('playtypeid') == 1

    utcnow = datetime.datetime.utcnow()
    begin_time = utcnow - datetime.timedelta(seconds=window)

    songs = []

    response = requests.get(KEXP_API, {'begin_time': begin_time}).json()
    while response.get('results'):
        songs.extend(Play.from_api(result) for result in response['results'] if is_song_play(result))
        response = requests.get(response['next']).json()  # this will throw KeyError if api response is malformed, but it looks like it always provides a next parameter even if the current response is empty

    return songs


def fetch_play(playid):
    response = requests.get(KEXP_API, {'playid': playid}).json()

    if not response.get('results'):
        return None

    return Play.from_api(response['results'][0])
