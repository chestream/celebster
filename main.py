# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, make_response, session, jsonify, redirect, url_for
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic

from flask_oauthlib.client import OAuth

from config import CONFIG
from firebase import firebase

firebase = firebase.FirebaseApplication('https://cefy.firebaseio.com', None)

app = Flask(__name__)
app.secret_key = 'development'

# Instantiate Authomatic.
authomatic = Authomatic(CONFIG, 'your secret string', report_errors=False)
oauth = OAuth(app)

from parse_rest.connection import register
from parse_rest.datatypes import Object, GeoPoint
from parse_rest.user import User


class cefy(Object):
    pass

linkedin = oauth.remote_app(
    'linkedin',
    consumer_key=CONFIG['linkedin']['consumer_key'],
    consumer_secret=CONFIG['linkedin']['consumer_secret'],
    request_token_params={
        'scope': 'r_basicprofile,r_emailaddress',
        'state': 'RandomString',
    },
    base_url='https://api.linkedin.com/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
)

google = oauth.remote_app(
    'google',
    consumer_key=CONFIG['google']['consumer_key'],
    consumer_secret=CONFIG['linkedin']['consumer_secret'],
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/')
def index():
    """
    Home handler
    """
    
    return render_template('index.html')


@app.route('/login/<provider_name>/', methods=['GET', 'POST'])
def login(provider_name):
    """
    Login handler, must accept both GET and POST to be able to use OpenID.
    """
    
    if provider_name == 'linkedin':
        return linkedin.authorize(callback=url_for('authorized_linkedin', _external=True))


    if provider_name == 'google':
        return google.authorize(callback=url_for('authorized_google', _external=True))


    # We need response object for the WerkzeugAdapter.
    response = make_response()
    
    # Log the user in, pass it the adapter and the provider name.
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)
    
    # If there is no LoginResult object, the login procedure is still pending.
    if result:
        if result.user:
            # We need to update the user to get more info.
            result.user.update()
        
        if provider_name == 'tw':
            user_data = result.user.data
            tweets = result.provider.access('https://api.twitter.com/1.1/statuses/user_timeline.json?count=1000').data
            favorites = result.provider.access('https://api.twitter.com/1.1/favorites/list.json?count=1000').data
            mentions = result.provider.access('https://api.twitter.com/1.1/statuses/mentions_timeline.json?count=1000').data
            messages = result.provider.access('https://api.twitter.com/1.1/direct_messages/sent.json?count=1000').data
            following = result.provider.access('https://api.twitter.com/1.1/friends/ids.json').data
            lists = result.provider.access('https://api.twitter.com/1.1/lists/list.json').data

            twitter_dict= {}
            twitter_dict['user_data'] = user_data
            twitter_dict['tweets'] = tweets
            twitter_dict['favorites'] = favorites
            twitter_dict['mentions'] = mentions
            twitter_dict['messages'] = messages
            twitter_dict['following'] = following
            twitter_dict['lists'] = lists

            

        # The rest happens inside the template.
        return render_template('login.html', result=result)
    
    # Don't forget to return the response.
    return response


@app.route('/login/authorized_linkedin')
def authorized_linkedin():
    resp = linkedin.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['linkedin_token'] = (resp['access_token'], '')
    me = linkedin.get('people/~:(id,first-name,last-name,headline,industry,num-connections,num-connections-capped,summary,specialties,positions,email-address,picture-url,location)')
    return jsonify(me.data)

@app.route('/login/authorized_google')
def authorized_google():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    return jsonify({"data": me.data})

@linkedin.tokengetter
def get_linkedin_oauth_token():
    return session.get('linkedin_token')

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

def change_linkedin_query(uri, headers, body):
    auth = headers.pop('Authorization')
    headers['x-li-format'] = 'json'
    if auth:
        auth = auth.replace('Bearer', '').strip()
        if '?' in uri:
            uri += '&oauth2_access_token=' + auth
        else:
            uri += '?oauth2_access_token=' + auth
    return uri, headers, body

linkedin.pre_request = change_linkedin_query

# Run the app.
if __name__ == '__main__':
    app.run(debug=True, port=8080)
