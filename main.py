# -*- coding: utf-8 -*-

from flask import Flask,g, render_template, request, make_response, session, jsonify, redirect, url_for,redirect
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic
import os
from flask_oauthlib.client import OAuth
import base64
import time
import tweepy
from config import CONFIG

from data_uri import DataURI

app = Flask(__name__)
app.secret_key = 'development'
app.config['UPLOAD_FOLDER'] = 'video_uploads/'

# Instantiate Authomatic.
authomatic = Authomatic(CONFIG, 'your secret string', report_errors=False)
oauth = OAuth(app)

from parse_rest.connection import register
from parse_rest.datatypes import Object, GeoPoint
from parse_rest.user import User

parse_credentials = {
    "application_id": "M5tnZk2K6PdF82Ra8485bG2VQwPjpeZLeL96VLPj",
    "rest_api_key": "VBGkzL4uHsOw0K1q33gHS4Qk2FWEucRHMHqT69ex",
    "master_key": "r9XwzOtLCoduZgmcU27Kc0sbexW4jWTOuBHStUFb",
}

register(parse_credentials["application_id"], parse_credentials["rest_api_key"])

SERVER_URL = ''

class celebster(Object):
    pass


class Bot():
    def __init__(self):
        self.consumer_key = 'qzfWazX1fmnkBLO8RKgWIQLgg'
        self.consumer_secret =  'ZQWbRLEYyHVhL3DswkluLdKvP1bVd46hnq1sxjiUH3SD6LljWm'
        self.access_token = '2999442824-jWuQzH3drHM4cIh2ZKAjNevebqMjZ6E1QkXD4yT'
        self.access_token_secret = 'SVHD6yZCkCejaVbYFZQ3kiSWM8LvzgoTErCYT6tsWbONU'
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(auth)

twitter = oauth.remote_app(
    'twitter',
    consumer_key='V6WiB2ogb1fr16W93wCO05rRR',
    consumer_secret='teUL3N96RYcXELar1FH9qy14LiW26kS0RD8UWprEm4vbNRWwRH',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/v',methods=['GET', 'POST'])
def video():  
    if request.method == 'GET':
        response = make_response()
    
        result = authomatic.login(WerkzeugAdapter(request, response), 'tw')
        if result:
            if result.user:
                result.user.update()
                file_name = ''
                return render_template('video2.html', result=result,file_name=file_name)
        
        return response

    else:
        #post endpoint for saving the video
        data_url = request.form['data_url']
        epoch = str(int(time.time()*100))
        file_name = '%s.webm'%epoch

        video_file = open(os.path.join(app.config['UPLOAD_FOLDER'], file_name), 'wb')
        # video_file.write(data_url)

        uri = DataURI(data_url)

        video_file.write(uri.data)
        return render_template('video2.html',file_name=file_name)


@app.route('/@/<username>/<objectId>')
def celebPage(username,objectId):
    return render_template('celeb.html',username=username,objectId=objectId)

@app.route('/celeblogin/<username>/<objectId>')
def celeblogin(username,objectId):
    response = make_response()
    
    result = authomatic.login(WerkzeugAdapter(request, response), 'tw')
    if result:
        if result.user:
            result.user.update()
            if result.user.username == username:
                c = celebster.Query.get(objectId=objectId)
                return render_template('player.html',c=c)
            else:
                return render_template('badlogin.html', result=result)
    return response


#todo send tweets from user's own profile
@app.route('/tweet', methods=['POST'])
def tweet():
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    status = request.form['tweet']
    if not status:
        return redirect(url_for('index'))
    resp = twitter.post('statuses/update.json', data={
        'status': status
    })
    if resp.status == 403:
        flash('Your tweet was too long.')
    elif resp.status == 401:
        flash('Authorization error with Twitter.')
    else:
        flash('Successfully tweeted your tweet (ID: #%s)' % resp.data['id'])
    return redirect(url_for('index'))

@app.route('/glogin')
def glogin():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/gtweet')
def gtweet():
    status_update = request.args.get('status')
    pleb = request.args.get('pleb')
    celeb = request.args.get('celeb')
    file_name = request.args.get('file_name')
    b = Bot()
    api = b.api

    v = celebster(pleb=pleb,celeb=celeb)
    v.save()

    our_url = " %s/@/%s/%s"%(SERVER_URL,celeb,v.objectId)
    status_update = status_update + our_url

    t = api.update_status(status=status_update)

    v.tweet_id = str(t.id)
    v.video_url = "http://%s/celebster/%s"%(SERVER_URL,file_name)
    v.save()

    return redirect('https://twitter.com/statuses/'+str(t.id))


@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


# Run the app.
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
