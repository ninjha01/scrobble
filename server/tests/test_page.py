from .helpers import TestCase


class TestPage(TestCase):
    def test_header(self):
        rv = self.client.get("/")
        assert "Play Scrobble" in str(rv.data)
