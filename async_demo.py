__author__ = 'steve'

import tornado.ioloop
import tornado.options
import tornado.web
from tornado import gen
from tornado.concurrent import Future

import os
import requests
from requests_oauthlib import OAuth1


from tornado.options import define, options
define('port', default=8000, help='run on the given port', type=int)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class TwitterHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        username = self.get_argument('username')
        if username:

            try:
                result = yield TwitterHandler.get_tweets(username)
            except Exception:
                pass
            else:
                self.render('twitter.html', twitters=result)
        else:
            self.redirect('/')

    @staticmethod
    def get_tweets(username):
        result_future = Future()
        """helper function to fetch 200 tweets for a user with @username
        """
        TWITTER_URL = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
        '''
        curl --get 'https://api.twitter.com/1.1/statuses/user_timeline.json' --data 'count=200&screen_name=twitterapi' --header 'Authorization: OAuth oauth_consumer_key="BlXj0VRgkpUOrN3b6vTyJu8YB", oauth_nonce="9cb4b1aaa1fb1d79e0fbd9bc8b33f82a", oauth_signature="SrJxsOCzOTnudKQMr4nMQ0gDuRk%3D", oauth_signature_method="HMAC-SHA1", oauth_timestamp="1456006969", oauth_token="701166849883373568-bqVfk8vajGxWIlKDe94CRjMJtBvwdQQ", oauth_version="1.0"' --verbose
        '''
        auth = OAuth1('BlXj0VRgkpUOrN3b6vTyJu8YB', 'qzkhGeWIYVXod9umMuinHF2OFmJxiucQspX5JsA7aH8xs5t4DT',
                      '701166849883373568-bqVfk8vajGxWIlKDe94CRjMJtBvwdQQ', 'y3gx0F5fLyIQQFNDev8JtpPKpEUmyy3mMibxCcTK2kbZZ')

        data = {'count': 200,
                'screen_name': username}

        r = requests.get(url=TWITTER_URL, params=data, auth=auth)
        data = r.json()

        if 'errors' in data:
            raise Exception
        res = []
        for item in data:
            if 'retweeted_status' not in item.keys():
                res.append(item)
        result_future.set_result(res)
        return result_future


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[
        (r"/", IndexHandler),
        (r"/twitter/", TwitterHandler),
    ], template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"))
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
