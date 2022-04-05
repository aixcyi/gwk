# -*- coding: utf-8 -*-

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


class URL:
    scheme: str = ''  # protocol
    host: str = ''  # domain
    path: str = ''
    params: str = ''
    query: dict = {}
    fragment: str = ''

    def __init__(self, url: str):
        self.scheme, self.host, self.path, self.params, q, f = urlparse(url)
        self.query = parse_qs(q)
        self.fragment = f

    def __str__(self):
        return urlunparse((
            self.scheme, self.host, self.path, self.params,
            urlencode(self.query), self.fragment
        ))
