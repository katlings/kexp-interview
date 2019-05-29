import json
from pathlib import Path

import mock

from django.test import TestCase
from django.urls import reverse

from .models import Comment
from .utils import add_comments_from_db, fetch_plays, fetch_plays_from_api, Play


class MockResponse:
    """
    Looks like the response from a live API call, but actually returns data
    from a stored json file. Used in place of a response from requests.get()
    """
    filename = None  # to be provided by subclasses

    def __init__(self, url, *args, **kwargs):
        self.url = url

    def json(self):
        # hack so we don't keep returning the same data when calling the next page
        # of the API
        if self.url == 'EOF':
            return {}

        with open(self.filename) as f:
            json_response = json.loads(f.read())
        json_response['next'] = 'EOF'
        return json_response

class MockSampleResponse(MockResponse):
    filename = Path(__file__).parent / 'testdata' / 'data-sample.json'

class MockDuplicateResponse(MockResponse):
    filename = Path(__file__).parent / 'testdata' / 'data-duplicates.json'

class MockMissingAlbumResponse(MockResponse):
    filename = Path(__file__).parent / 'testdata' / 'data-noalbum.json'


class PlaylistViewTests(TestCase):
    @mock.patch('requests.get', MockSampleResponse)
    def test_api_parsing(self):
        """
        General tests to see if parsing API response into play data acts as expected
        """
        plays = fetch_plays()
        # Assert we've filtered out air breaks to come up with 14 songs played
        self.assertIs(len(plays), 14)
        # Assert most recent play with the highest ID is at the start
        self.assertIs(plays[0].playid > plays[-1].playid, True)
        self.assertEqual(plays[0].title, 'Due West')

    @mock.patch('requests.get', MockDuplicateResponse)
    def test_no_duplicate_tracks(self):
        """
        Test that we can successfully deduplicate tracks in the anecdotally rare
        situation where they are returned by the API
        """
        # use dummy values for begin and end times
        nonunique_plays = fetch_plays_from_api(None, None)
        plays = fetch_plays()

        all_titles = sorted([play.title for play in plays])
        nonunique_titles = sorted([play.title for play in nonunique_plays])
        self.assertNotEqual(all_titles, nonunique_titles)

        unique_titles = sorted(list(set(all_titles)))
        unique_titles_from_api = sorted(list(set(nonunique_titles)))
        self.assertEqual(all_titles, unique_titles)
        self.assertEqual(unique_titles, unique_titles_from_api)

    @mock.patch('requests.get', MockMissingAlbumResponse)
    def test_no_album_works(self):
        """
        Test that we can handle it when album data is not provided
        """
        plays = fetch_plays()
        self.assertIs(len(plays), 1)
        self.assertEqual(plays[0].title, 'Face the Fire')
        self.assertEqual(plays[0].artist, 'Boy Harsher')
        self.assertIs(plays[0].album, None)

    def test_comment(self):
        """
        Test retrieving a comment on a single song
        """
        playid = 42
        comment_text = 'This is my favorite band'
        comment = Comment(playid=playid, comment=comment_text)
        comment.save()

        play = Play(42, 'Ticket to Ride', 'The Beatles', 'Help!', '2019-05-28T11:11:11Z')

        plays_with_comments = add_comments_from_db([play])
        self.assertIs(len(plays_with_comments), 1)
        self.assertEqual(plays_with_comments[0].comment, comment_text)

    def test_comments(self):
        """
        Test retrieving comments correctly on a set of songs
        """
        playid = 42
        comment_text = 'This is my favorite band'
        comment = Comment(playid=playid, comment=comment_text)
        comment.save()

        playid2 = 55
        comment_text2 = 'This is my other favorite band'
        comment = Comment(playid=playid2, comment=comment_text2)
        comment.save()

        plays = [Play(42, 'Ticket to Ride', 'The Beatles', 'Help!', '2019-05-28T11:11:11Z'),
                 Play(50, 'Fire Drills', 'Dessa', 'Chime', '2019-05-28T11:15:11Z'),
                 Play(55, 'Vicious', 'Halestorm', 'Vicious', '2019-05-28T11:19:11Z'),
                ]
        self.assertIs(None, plays[0].comment)

        plays_with_comments = add_comments_from_db(plays)

        self.assertIs(len(plays_with_comments), 3)
        self.assertEqual(comment_text, plays_with_comments[0].comment)
        self.assertIs(None, plays_with_comments[1].comment)
        self.assertEqual(comment_text2, plays_with_comments[2].comment)
