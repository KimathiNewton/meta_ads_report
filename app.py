from flask import Flask, jsonify, session, redirect, request, url_for
from flask_oauthlib.client import OAuth
import requests
import json
import logging
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


FACEBOOK_APP_ID = '1078321516555226'
FACEBOOK_APP_SECRET = 'e1f8be49eb86864a6a8c3babe64ac654'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
SCOPES = 'read_orders'
BASE_URL = "https://graph.facebook.com/"
API_VERSION = "2024-01"


app = Flask(__name__)
app.secret_key = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['AUTHLIB_INSECURE_TRANSPORT'] = 1
 
oauth = OAuth(app)
facebook = oauth.remote_app(
    'facebook',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'},
    base_url=BASE_URL,
    request_token_url=None,
    access_token_method='POST',
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
)

@app.route('/')
def index():
    return 'Welcome to your Flask Facebook App!'

@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('authorized', _external=True, _scheme='http'))

@app.route('/logout')
def logout():
    session.pop('facebook_token', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    response = facebook.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['facebook_token'] = response.get('access_token', '')

    return {
        "message": "success"
    }

def authenticate_facebook():
    try:
        graph = facebook.get('me/accounts')
        accounts = graph.data
        if accounts and accounts[0].get('id'):
            ad_account_id = accounts[0]['id']  # Assuming the first account is the ad account
            ad_account = graph.get(ad_account_id)
            return ad_account.data
        else:
            return None
    except Exception as e:
        print(f"Error authenticating with Facebook: {e}")
        return None

def fetch_campaign_data(ad_account, start_date, end_date):
    fields = ['campaign_name', 'reach', 'spend', 'clicks', 'impressions', 'actions', 'post_engagement', 'post_comments', 'post_likes', 'post_shares']
    params = {
        'time_range': {'since': start_date, 'until': end_date},
        'level': 'campaign',
        'filtering': [{'field': 'objective', 'operator': 'IN', 'value': ['POST_ENGAGEMENT', 'REACH', 'VIDEO_VIEWS', 'IMPRESSIONS', 'LINK_CLICKS']}],
        'breakdowns': ['placement'],
        'fields': ','.join(fields)
    }
    insights = ad_account.get_insights(fields=fields, params=params)
    campaign_data = [insight for insight in insights]

    for campaign in campaign_data:
        campaign['spend'] = round(campaign['spend'], 2)

    return campaign_data

@app.route('/extract-data', methods=['GET', 'POST'])
def extract_data():
    access_token = session.get('facebook_token')
    if not access_token:
        return jsonify({'error': 'Access token not found'})

    ad_account = authenticate_facebook()

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
    else:
        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")

    campaign_data = fetch_campaign_data(ad_account, start_date, end_date)

    if campaign_data:
        with open('campaign_data.json', 'w') as f:
            json.dump(campaign_data, f)

        return jsonify({'message': 'Data extraction successful. Check campaign_data.json for the results.'})
    else:
        return jsonify({'error': 'Failed to fetch campaign data'})
    
if __name__ == "__main__":
    app.run(debug=True)