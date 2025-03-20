# scrapers/__init__.py - Make scrapers directory a package and enable easier imports

from .base import BaseScraper
from .wikipedia import WikipediaScraper
from .discogs import DiscogsScraper
from .musicbrainz import MusicBrainzScraper

__all__ = [
    'BaseScraper',
    'WikipediaScraper',
    'DiscogsScraper',
    'MusicBrainzScraper',
]