#!/usr/bin/python
import oauth2 as oauth
import warnings
warnings.simplefilter('ignore', DeprecationWarning)
"""
Saves your tweets to a local file
"""

import httplib2, urllib, time, sys, re
try:
    import json
except ImportError:
    import simplejson as json


# Valid options for TIMELINE or -m, and the corresponding endpoints at twitter.com/statuses/ and the local filenames we use.
timelines = {
    'user': {
        'remote': 'statuses/user_timeline',
        'local': 'my_tweets'
    },
    'friends': {
        'remote': 'statuses/home_timeline',
        'local': 'my_friends_tweets'
    },
    'mentions': {
        'remote': 'statuses/mentions_timeline',
        'local': 'mentions'
    },
    'direct': {
        'remote': 'direct_messages',
        'local': 'direct'
    },
    'direct-sent': {
        'remote': 'direct_messages/sent',
        'local': 'direct-sent'
    },
    'favorites': {
        'remote': 'favorites/list',
        'local': 'favourites'
    }
}


if '-k' in sys.argv and '-s' in sys.argv and '-o' in sys.argv and '-e' in sys.argv:
    CONSUMER_KEY = sys.argv[sys.argv.index('-k')+1]
    CONSUMER_SECRET = sys.argv[sys.argv.index('-s')+1]
    ACCESS_TOKEN = sys.argv[sys.argv.index('-o')+1]
    ACCESS_TOKEN_SECRET = sys.argv[sys.argv.index('-e')+1]
else:
    try:
        from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
    except ImportError:
        print "Keys and tokens not specified. Create a config.py file or use the -k, -s, -o and -e command line options"
        sys.exit(1)


# Work out whether we're doing user_timeline or friends_timeline.
TIMELINE = 'user'
if '-m' in sys.argv:
    TIMELINE = sys.argv[sys.argv.index('-m')+1]
else:
    try:
        from config import TIMELINE
    except ImportError:
        pass
try:
    REMOTE_TIMELINE = "https://api.twitter.com/1.1/%s.json" % timelines[TIMELINE]['remote']
except KeyError:
    print "Invalid timeline: ", TIMELINE
    sys.exit(1)
FILE = timelines[TIMELINE]['local']


if '-t' in sys.argv:
    FILE = "%s.txt" % FILE
    import pickle
    
    def load_all():
        try:
            return pickle.load(open(FILE))
        except IOError:
            return []
    
    def write_all(tweets):
        pickle.dump(tweets, open(FILE, 'w'))
else:
    FILE = "%s.json" % FILE
    
    def load_all():
        try:
            return json.load(open(FILE))
        except IOError:
            return []
    
    def write_all(tweets):
        json.dump(tweets, open(FILE, 'w'), indent = 2)

if '-f' in sys.argv:
    FILE_PATH = sys.argv[sys.argv.index('-f')+1]
else:
    try:
        from config import FILE_PATH
    except ImportError:
        print "File_path not specified. Create a config.py file or use the -f command line options"
        sys.exit(1)
    
FILE = FILE_PATH + FILE
    

def normalize_url(url):
    # Simple length heuristic
    if len(url) < 10: return None

    # Make sure we have some sort of protocol
    if not re.search('://', url):
        url = 'http://' + url

    return url

def lookup_short_urls(tweet):
    # If short_urls are already there, skip
    if 'short_urls' in tweet: return

    # (Start of line or word)
    # (Maybe something like http://)
    # (A vaguely domain-like section, at least one dot which is not a double dot)
    # (Whatever else follows, liberally via non-whitespace)
    url_regex = '(\A|\\b)([\w-]+://)?\S+[.][^\s.]\S*'

    redir = httplib2.Http(timeout=10)
    redir.follow_redirects = False
    redir.force_exception_to_status_code = True

    short_urls = {}

    new_text = tweet['text']
    for sub in tweet['text'].split():
        orig_url_match = re.search(url_regex, sub)
        if not orig_url_match:
            continue
        orig_url = normalize_url(orig_url_match.group(0))
        if not orig_url: continue

        try:
            response = redir.request(orig_url)[0]
            if 'status' in response and response['status'] == '301':
                short_urls[response['location']] = orig_url
                new_text = new_text.replace(orig_url, response['location'])
        except:
            pass

    tweet['short_urls'] = short_urls
    tweet['text'] = new_text

def fetch_and_save_new_tweets():
    tweets=load_all()
    old_tweet_ids = set(t['id'] for t in tweets)
    if tweets:
        since_id = max(t['id'] for t in tweets)
    else:
        since_id = None
    try:
        new_tweets = fetch_all(since_id)
    except ValueError, msg:
        print "An error occurred while getting your tweets: ", msg
        sys.exit(1)
    num_new_saved = 0
    for tweet in new_tweets:
        if tweet['id'] not in old_tweet_ids:
            tweets.append(tweet)
            num_new_saved += 1
    tweets.sort(key = lambda t: t['id'], reverse=True)
    # Delete the 'user' key (unless this is the friends' timeline), lookup short URLs
    for t in tweets:
        if TIMELINE == 'user' and 'user' in t:
            del t['user']
        lookup_short_urls(t)
    # Save back to disk
    write_all(tweets)
    print "Saved %s new tweets" % num_new_saved

def fetch_all(since_id = None):
    all_tweets = []
    seen_ids = set()
    page = 0
    args = {'count': 200}
    if since_id is not None:
        args['since_id'] = since_id

    all_tweets_len = len(all_tweets)

    while True:
        args['page'] = page

        # Via http://blog.yjl.im/2010/04/first-step-to-twitter-oauth-streaming.html
        consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
        token = oauth.Token(key=ACCESS_TOKEN, secret=ACCESS_TOKEN_SECRET)
        client = oauth.Client(consumer, token)
        resp, content = client.request("%s?%s" % (REMOTE_TIMELINE, urllib.urlencode(args)), 'GET')

        if resp['status'] == '502':
            # This usually seems to mean the request has timed out, but if we try again
            # the result has been cached and will work second time round.
            time.sleep(2)
            resp, content = client.request("%s?%s" % (REMOTE_TIMELINE, urllib.urlencode(args)), 'GET')

        page += 1
        tweets = json.loads(content)
        if 'errors' in tweets:
            raise ValueError, tweets['errors'][0]['message'] + ' (code ' + str(tweets['errors'][0]['code']) + ')'
        if not tweets:
            break
        for tweet in tweets:
            if tweet['id'] not in seen_ids:
                seen_ids.add(tweet['id'])
                all_tweets.append(tweet)
        all_tweets_len = len(all_tweets)
        time.sleep(2)

    all_tweets.sort(key = lambda t: t['id'], reverse=True)
    return all_tweets



if __name__ == '__main__':
    fetch_and_save_new_tweets()
