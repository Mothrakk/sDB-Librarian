# sDB Librarian

This application will fetch your Steam library, memorizes every game you own, then opens https://steamdb.info/sales/ and returns back x amount of games that you do not already own. Uses Selenium and PhantomJS for the dirty JavaScript work.

I sometimes look for new games to buy, and Steam's front page only lists me Borderlands i for i in range(infinity). This is a solution to that.

Features returning of category-specific games, sorted by relevance. If no categories are given, then sorts games by SteamDB's rating algorithm.

Also included is a compiled version.

## Credits

BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/

lxml parser: http://lxml.de/parsing.html

PhantomJS: http://phantomjs.org/

Requests: http://docs.python-requests.org/en/master/

Selenium: http://selenium-python.readthedocs.io/

## Notice

This only semi-works and is of horrible quality. It uses Selenium when it could easily work with simple API calls. It's complete spaghetti and I mostly made this for practice when having discovered Selenium. I'm still leaving it up here for note.

Works as a proof of concept.
