import os
from dataclasses import dataclass
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
load_dotenv()

class FirebaseAuthError(Exception):
    pass

@dataclass
class AuthenticatedUser:
    uid: str
    email: str
    display_name: str | None
    photo_url: str | None
    id_token: str
    refresh_token: str
    expires_in: int

class FirebaseAuthService:
    FIREBASE_SIGN_IN_URL = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp'
    GOOGLE_SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']

    # Load the Firebase and Google OAuth settings.
    def __init__(self, credentials_file: str='credentials/google_oauth_client.json'):
        self.credentials_file = credentials_file
        self.firebase_api_key = os.getenv('FIREBASE_API_KEY')
        if not self.firebase_api_key:
            raise FirebaseAuthError('FIREBASE_API_KEY is missing from .env')

    # Run Google sign-in and return a Firebase-authenticated user.
    def login(self) -> AuthenticatedUser:
        google_id_token = self._google_login()
        firebase_data = self._exchange_google_token(google_id_token)
        return AuthenticatedUser(uid=firebase_data['localId'], email=firebase_data.get('email', ''), display_name=firebase_data.get('displayName'), photo_url=firebase_data.get('photoUrl'), id_token=firebase_data['idToken'], refresh_token=firebase_data['refreshToken'], expires_in=int(firebase_data.get('expiresIn', 3600)))

    # Open the browser login flow and get the Google ID token.
    def _google_login(self) -> str:
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, scopes=self.GOOGLE_SCOPES)
            credentials = flow.run_local_server(port=0, open_browser=True, prompt='select_account')
        except Exception as error:
            raise FirebaseAuthError(f'Google login failed: {error}') from error
        google_id_token = credentials.id_token
        if not google_id_token:
            raise FirebaseAuthError('Google did not return an ID token.')
        return google_id_token

    # Exchange the Google token for Firebase authentication tokens.
    def _exchange_google_token(self, google_id_token: str) -> dict:
        endpoint = f'{self.FIREBASE_SIGN_IN_URL}?key={self.firebase_api_key}'
        post_body = urlencode({'id_token': google_id_token, 'providerId': 'google.com'})
        payload = {'requestUri': 'http://localhost', 'postBody': post_body, 'returnSecureToken': True, 'returnIdpCredential': True}
        try:
            response = requests.post(endpoint, json=payload, timeout=15)
            response.raise_for_status()
        except requests.HTTPError as error:
            try:
                details = error.response.json()
            except Exception:
                details = error.response.text
            raise FirebaseAuthError(f'Firebase authentication failed: {details}') from error
        except requests.RequestException as error:
            raise FirebaseAuthError(f'Could not connect to Firebase Authentication: {error}') from error
        data = response.json()
        if not data.get('idToken'):
            raise FirebaseAuthError('Firebase did not return an ID token.')
        return data
