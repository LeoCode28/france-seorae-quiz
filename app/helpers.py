"""Small helpers: email validation, session bootstrap, admin gate, media proxy."""
import re
import urllib.parse
import urllib.request

from flask import Response, abort, request, session

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def email_valid(e: str) -> bool:
    return bool(_EMAIL_RE.match(e))


def init_session() -> None:
    """Ensure the base session keys exist."""
    if 'reponses_ids' not in session:
        session['reponses_ids'] = []
        session['score'] = 0


def admin_required() -> bool:
    return session.get('admin_ok', False)


def proxy_img(url: str) -> str:
    """Build a proxied URL for a Google-hosted image."""
    return '/media-proxy?url=' + urllib.parse.quote(url, safe='')


def media_proxy_view():
    """Proxy Google-hosted images to bypass referrer/CORS restrictions.

    Registered as a plain Flask view (not a blueprint route) so other
    blueprints can import `proxy_img` freely without circular imports.
    """
    url = request.args.get('url', '')
    if not url or not url.startswith('https://'):
        abort(404)
    host = urllib.parse.urlparse(url).hostname or ''
    allowed = ('googleusercontent.com', 'google.com', 'ggpht.com',
               'googleapis.com')
    if not any(host.endswith(h) for h in allowed):
        abort(403)
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; FranceSeorae/1.0)'
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            ctype = resp.headers.get('Content-Type', 'image/jpeg')
        return Response(data, content_type=ctype, headers={
            'Cache-Control': 'public, max-age=86400',
        })
    except Exception as e:
        print(f'[proxy] ❌ Failed: {url[:120]} — {e}')
        abort(502)
