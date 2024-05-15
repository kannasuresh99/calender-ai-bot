import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import openai
from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

# Load credentials from file
with open('credentials.json', 'r') as file:
    credentials_info = json.load(file)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Initialize OpenAI API
openai.api_key = 'your_openai_api_key'

# Sample event data (replace with actual event data)
events_data = [
    {'summary': 'Meeting with Client', 'description': 'Discuss project updates.', 'start_time': '2024-05-15T10:00:00Z', 'end_time': '2024-05-15T11:00:00Z', 'keywords': ['Meeting', 'Client', 'Discuss', 'Project', 'Updates']},
    {'summary': 'Lunch Break', 'description': 'Take a break and relax.', 'start_time': '2024-05-15T12:00:00Z', 'end_time': '2024-05-15T13:00:00Z', 'keywords': ['Lunch', 'Break', 'Relax']}
]

# Preprocess event data
def preprocess_event(event):
    summary = event.get('summary', '')
    description = event.get('description', '')
    start_time = event['start'].get('dateTime', event['start'].get('date', ''))
    end_time = event['end'].get('dateTime', event['end'].get('date', ''))

    # Extract keywords using regex or NLP techniques
    keywords = re.findall(r'\b\w{3,}\b', summary + ' ' + description)

    return {
        'summary': summary,
        'description': description,
        'start_time': start_time,
        'end_time': end_time,
        'keywords': keywords
    }

preprocessed_data = [preprocess_event(event) for event in events_data]

# Extract text for vectorization
text_data = [' '.join(event['keywords']) for event in preprocessed_data]

# Initialize TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer()

# Fit and transform the text data
tfidf_matrix = tfidf_vectorizer.fit_transform(text_data)

# Get feature names (terms)
feature_names = tfidf_vectorizer.get_feature_names_out()

# Convert TF-IDF matrix to a list of dictionaries
tfidf_data = [dict(zip(feature_names, row.toarray()[0])) for row in tfidf_matrix]

# Initialize Google Calendar API
def get_calendar_service(credentials):
    credentials = google.oauth2.credentials.Credentials(**credentials)
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
    return service

@app.route('/')
def index():
    return 'Welcome to the Calendar Chatbot!'

@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        credentials_info,
        scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    session['state'] = state

    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        credentials_info,
        scopes=SCOPES,
        state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('query_calendar'))

@app.route('/query_calendar')
def query_calendar():
    if 'credentials' not in session:
        return redirect('authorize')

    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])

    service = get_calendar_service(credentials)

    # Call the Calendar API
    events_result = service.events().list(calendarId='primary', timeMin='2024-05-15T00:00:00Z',
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    return jsonify(events)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_query = data.get('question')

    # Concatenate vectorized data with user query
    prompt = f"Data: {tfidf_data}\n\nUser Query: {user_query}\n\nAnswer:"

    # Use OpenAI to process the prompt
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150
    )

    answer = response.choices[0].text.strip()

    return jsonify({'answer': answer})

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

if __name__ == '__main__':
    app.run('localhost', 8080, debug=True)
