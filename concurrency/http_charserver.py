#!/usr/bin/env python3

import asyncio
from aiohttp import web

from charfinder import UnicodeNameIndex

PAGE_TPL = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Charserver</title>
  </head>
  <body>
    <p>
        <form action="/">
          <input type="search" name="query" value="{query}">
          <input type="submit" value="find">
        Examples: {links}
        </form>
    </p>
    <p>{message}</p>
    <hr>
  <pre>
{result}
  </pre>
  </body>
</html>
'''

CONTENT_TYPE = 'text/html; charset=UTF-8'

EXAMPLE_WORDS = ('chess cat circled Malayalam digit Roman face Ethiopic'
                 ' black mark symbol dot operator Braille hexagram').split()
LINK_TPL = '<a href="/?query={0}" title="find &quot;{0}&quot;">{0}</a>'

index = None  # a UnicodeNameIndex instance


@asyncio.coroutine
def handle(request):
    query = request.GET.get('query', '')
    print('Query: {!r}'.format(query))
    if query:
        lines = list(index.find_descriptions(query))
        res = '\n'.join(lines)
        msg = index.status(query, len(lines))
    else:
        lines = []
        res = ''
        msg = 'Type words describing characters.'

    links = ', '.join(LINK_TPL.format(word)
                      for word in sorted(EXAMPLE_WORDS, key=str.upper))
    text = PAGE_TPL.format(query=query, result=res,
                           message=msg, links=links)
    return web.Response(content_type=CONTENT_TYPE, text=text)


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', handle)

    server = yield from loop.create_server(app.make_handler(),
                                           '127.0.0.1', 8080)
    host = server.sockets[0].getsockname()
    print('Serving on {}. Hit CTRL-C to stop.'.format(host))


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()


if __name__ == '__main__':
    index = UnicodeNameIndex()
    main()