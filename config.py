# config.py

from authomatic.providers import oauth2, oauth1, openid

CONFIG = {
    
    'tw': { # Your internal provider name
           
        # Provider class
        'class_': oauth1.Twitter,
        
        # Twitter is an AuthorizationProvider so we need to set several other properties too:
        'consumer_key': 'V6WiB2ogb1fr16W93wCO05rRR',
        'consumer_secret': 'teUL3N96RYcXELar1FH9qy14LiW26kS0RD8UWprEm4vbNRWwRH',
    },
    
    'fb': {
           
        'class_': oauth2.Facebook,
        
        # Facebook is an AuthorizationProvider too.
        'consumer_key': '1529132127366244',
        'consumer_secret': 'f3a21526aa509d31d2d5a676c69c4b18',
        
        # But it is also an OAuth 2.0 provider and it needs scope.
        'scope': ['user_about_me', 'email', 'user_posts'],
    },

    'google':{
        'consumer_key': '232011260217-tlne4qmr49lmij38it4pe82nr0jda4n8.apps.googleusercontent.com',
        'consumer_secret' : 'BiCm553aQGxJAETWEsP5uRHE'

    },

    'linkedin':{
        'consumer_key': '75p6gl1raqe2f6',
        'consumer_secret': 'jMQ83UFPXqBgQ5QR'
    },
    
    'oi': {
           
        # OpenID provider dependent on the python-openid package.
        'class_': openid.OpenID,
    }
}



'''

Google dash: https://console.cloud.google.com/apis/credentials?project=cefy-1218&authuser=3
Twitter dash: 
LinkedIN dash: https://www.linkedin.com/developer/apps/4788841/auth 
Facebook dash:
Instagram dash:


'''