#mytweets

Forked by Phil Gyford  
phil@gyford.com

This is a fork of simonw's original mytweets script:  
http://github.com/simonw/mytweets/tree/master
via http://github.com/blech/mytweets

mytweets is a script to back up all your (and/or your friends') tweets to 
local files. It can save them in JSON or Python's pickle format. Subsequent
runs will fetch tweets since the last run and add them to the file(s).

Now works with the Twitter API v1.1.

## Notes

1. mytweets requires python-oauth2 from 
   http://github.com/simplegeo/python-oauth2
2. python-oauth2 in turn requires httplib2 from http://code.google.com/p/httplib2/
3. mytweets requires simplejson (unless Python 2.6) from 
   http://pypi.python.org/pypi/simplejson/

(or use the [pip](https://pypi.python.org/pypi/pip) `REQUIREMENTS.txt` file)


## Directions

1. Put `fetch.py` in any directory

2. Run `chmod +x fetch.py`

3. Set up your Twitter account with a new app:
   1. Go to http://dev.twitter.com/ and log in with your Twitter account.
   2. Go to 'My applications', in the drop-down menu under your icon, top-right.
   3. Click the 'Create a new application' button.
   4. Fill out the form.
        * Set 'Name' (it won't be publicly visible unless 
          you also use this app to post tweets).
		* Set 'Description' (it's required).
        * Set 'Website' to some URL (it's required).
		* Agree with the terms and submit the form.

4. By default the application will be 'Read-only'. If you want to access direct 
   messages then go to the 'Settings' tab and change the 'Application Type' to 
   'Read, Write and Access direct messages'.

5. At the bottom of the 'Details' tab page, click the 'Create my access token' 
   button. You might need to refresh the page once or twice after that before the 
   new token appears.

6. Create a file called `config.py` in the same directory as the `fetchy.py`
   script. Copy and paste the 'Consumer key', 'Consumer secret', 'Access token' and
   'Access token secret' into it in this format:

        CONSUMER_KEY = 'Esdfy8iSDF89vdaDFSa789'
        CONSUMER_SECRET = 'DFYUK89fddsfadFDDFS789vsdCXUdfs789xcvDSFH'
        ACCESS_TOKEN = '74382-89FDSHJKjkdsfsfFDSY89SFDFES8978dfsfsda78fdl'
        ACCESS_TOKEN_SECRET = '0dfsYFDSs789SDF7uyfdshjksdf789SFSDFHJKSDF'
    
   Or else you can use the `-k`, `-s`, `-o`, `-e` options on the command line.

7. Add the `FILE_PATH` to where you want the resulting file of tweets to be 
   saved, into `config.py`: 

        FILE_PATH = '/path/to/the/file/we/will/create/'

   or use the `-f` option on the command line.
   
8. Optionally add the TIMELINE argument which can be one of `user`  
   (default), `friends`, `mentions`, `direct`, `direct-sent`, `favorites` into 
   `config.py`:

        TIMELINE = 'friends'
    
   or use the `-m` option on the command line.

8. Run the command like so:

        ./fetch.py [-k your-consumer-key -s your-consumer-secret \
            -o your-access-token -e your-access-token-secret \
            -f /path/to/the/file/we/will/create/ \
            -m [user|friends|mentions|direct|direct-sent|favorites]] [-t]
   
   ie, if all your config settings are in `config.py` you'll only need to do
   something like:

        ./fetch.py -m friends
   
   It can take a long time to run first time round as later pages of 
   results can take a long time to be returned from Twitter.
   
9. Run the command again at any time to save any tweets created since you 
   last ran the script.

