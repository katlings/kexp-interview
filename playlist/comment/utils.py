import datetime
import requests


KEXP_API = 'https://legacy-api.kexp.org/play/'


class Play:
    def __init__(self, playid, title, artist, album):
        self.playid = playid
        self.title = title
        self.artist = artist
        self.album = album

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
        return f'{self.title} by {self.artist} from {self.album}'


def fetch_songs(window=3600):
    """
    Fetch the songs that were played on KEXP in the last [window] seconds
    
    Return in a simplified format as a list of Play objects
    """

    def is_song_play(playdict):
        return playdict.get('playtype', {}).get('playtypeid') == 1

    utcnow = datetime.datetime.utcnow()
    songs_since = utcnow - datetime.timedelta(seconds=window)

    songs = []

    # TODO: try/catch
    response = requests.get(KEXP_API, {'begin_time': songs_since}).json()
    while response.get('results'):
        songs.extend(Play.from_api(result) for result in response['results'] if is_song_play(result))
        response = requests.get(response['next']).json()  # this will throw keyerror if api response is malformed, but it looks like it always provides a next parameter

    return songs
