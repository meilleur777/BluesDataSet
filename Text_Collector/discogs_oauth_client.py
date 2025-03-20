import os
import time
import random
import string
import requests
import urllib.parse
import dotenv

class DiscogsOAuthClient:
    """Complete Discogs OAuth implementation following Discogs API specifications"""

    def __init__(self, env_file=".env"):
        # Load credentials from .env file
        dotenv.load_dotenv(env_file)

        # API endpoints
        self.api_url = "https://api.discogs.com"
        self.request_token_url = f"{self.api_url}/oauth/request_token"
        self.authorize_url = "https://discogs.com/oauth/authorize"
        self.access_token_url = f"{self.api_url}/oauth/access_token"
        self.identity_url = f"{self.api_url}/oauth/identity"

        # Get credentials from environment
        self.consumer_key = os.getenv("DISCOGS_CONSUMER_KEY")
        self.consumer_secret = os.getenv("DISCOGS_CONSUMER_SECRET")
        self.user_agent = os.getenv("DISCOGS_USER_AGENT")

        if not self.consumer_key or not self.consumer_secret or not self.user_agent:
            raise ValueError("DISCOGS_CONSUMER_KEY, DISCOGS_CONSUMER_SECRET, and DISCOGS_USER_AGENT must be set in key.env file")

        # Set callback URL (can be out-of-band for desktop apps)
        self.callback_url = os.getenv("DISCOGS_CALLBACK_URL", "oob")

        # Storage for tokens
        self.request_token = None
        self.request_token_secret = None
        self.access_token = None
        self.access_token_secret = None

    def generate_nonce(self, length=12):
        """Generate a random string for oauth_nonce"""
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    def get_request_token(self):
        """Step 2: Get OAuth request token using exact header format specified by Discogs"""

        # Generate required OAuth parameters
        oauth_timestamp = str(int(time.time()))
        oauth_nonce = self.generate_nonce()

        # Create Authorization header with exact format required
        auth_header = (
            'OAuth oauth_consumer_key="' + self.consumer_key + '", '
            'oauth_nonce="' + oauth_nonce + '", '
            'oauth_signature="' + self.consumer_secret + '&", '
            'oauth_signature_method="PLAINTEXT", '
            'oauth_timestamp="' + oauth_timestamp + '", '
            'oauth_callback="' + self.callback_url + '"'
        )

        # Set up headers as specified in documentation
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': auth_header,
            'User-Agent': self.user_agent
        }

        print("Sending request to get OAuth request token...")

        # Make the request
        response = requests.get(self.request_token_url, headers=headers)

        # Check for success
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Failed to get request token: {response.text}")

        # Parse the response
        response_params = urllib.parse.parse_qs(response.text)

        # Extract token and secret
        self.request_token = response_params.get('oauth_token', [''])[0]
        self.request_token_secret = response_params.get('oauth_token_secret', [''])[0]
        oauth_callback_confirmed = response_params.get('oauth_callback_confirmed', ['false'])[0]

        if oauth_callback_confirmed != 'true':
            raise Exception("OAuth callback was not confirmed by Discogs")

        print("✓ Request token obtained successfully")
        print(f"Request Token: {self.request_token}")

        return {
            'oauth_token': self.request_token,
            'oauth_token_secret': self.request_token_secret
        }

    def get_authorization_url(self):
        """Step 3: Generate authorization URL for user to visit"""
        if not self.request_token:
            raise ValueError("Must obtain request token before getting authorization URL")

        auth_url = f"{self.authorize_url}?oauth_token={self.request_token}"
        return auth_url

    def get_access_token(self, verifier):
        """Step 4: Exchange request token for access token"""
        if not self.request_token or not self.request_token_secret:
            raise ValueError("Must obtain request token before getting access token")

        # Generate required OAuth parameters
        oauth_timestamp = str(int(time.time()))
        oauth_nonce = self.generate_nonce()

        # Create Authorization header with exact format required
        auth_header = (
            'OAuth oauth_consumer_key="' + self.consumer_key + '", '
            'oauth_nonce="' + oauth_nonce + '", '
            'oauth_token="' + self.request_token + '", '
            'oauth_signature="' + self.consumer_secret + '&' + self.request_token_secret + '", '
            'oauth_signature_method="PLAINTEXT", '
            'oauth_timestamp="' + oauth_timestamp + '", '
            'oauth_verifier="' + verifier + '"'
        )

        # Set up headers as specified in documentation
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': auth_header,
            'User-Agent': self.user_agent
        }

        print("Exchanging request token for access token...")

        # Make the request
        response = requests.post(self.access_token_url, headers=headers)

        # Check for success
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Failed to get access token: {response.text}")

        # Parse the response
        response_params = urllib.parse.parse_qs(response.text)

        # Extract token and secret
        self.access_token = response_params.get('oauth_token', [''])[0]
        self.access_token_secret = response_params.get('oauth_token_secret', [''])[0]

        print("✓ Access token obtained successfully")

        return {
            'oauth_token': self.access_token,
            'oauth_token_secret': self.access_token_secret
        }

    def verify_identity(self):
        """Step 5: Verify authentication by checking identity"""
        if not self.access_token or not self.access_token_secret:
            raise ValueError("Must obtain access token before verifying identity")

        # Generate required OAuth parameters
        oauth_timestamp = str(int(time.time()))
        oauth_nonce = self.generate_nonce()

        # Create Authorization header
        auth_header = (
            'OAuth oauth_consumer_key="' + self.consumer_key + '",'
            'oauth_nonce="' + oauth_nonce + '", '
            'oauth_token="' + self.access_token + '", '
            'oauth_signature="' + self.consumer_secret + '&' + self.access_token_secret + '", '
            'oauth_signature_method="PLAINTEXT", '
            'oauth_timestamp="' + oauth_timestamp + '"'
        )

        # Set up headers
        headers = {
            'Authorization': auth_header,
            'User-Agent': self.user_agent
        }

        print("Verifying authentication with identity check...")

        # Make the request
        response = requests.get(self.identity_url, headers=headers)

        # Check for success
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Identity verification failed: {response.text}")

        # Parse the response
        user_data = response.json()

        print(f"✓ Authentication successful! Logged in as: {user_data.get('username')}")

        return user_data

    def complete_oauth_flow(self):
        """Complete the entire OAuth flow"""

        # Step 1: Load credentials (done in __init__)

        # Step 2: Get request token
        self.get_request_token()

        # Step 3: Get authorization URL
        auth_url = self.get_authorization_url()
        print(f"\nPlease visit this URL to authorize the application:")
        print(f"\n{auth_url}\n")
        print("After authorization, you will be given a verification code.")

        # Wait for verifier from user
        verifier = input("\nEnter the verification code: ")

        # Step 4: Exchange request token for access token
        access_tokens = self.get_access_token(verifier)

        # Step 5: Verify identity
        user_data = self.verify_identity()

        print("\n===============================")
        print("Authentication Complete!")
        print("===============================")
        print(f"Username: {user_data.get('username')}")
        print(f"User ID: {user_data.get('id')}")
        print("\nAccess Tokens (save these for future use):")
        print(f"DISCOGS_OAUTH_TOKEN={self.access_token}")
        print(f"DISCOGS_OAUTH_TOKEN_SECRET={self.access_token_secret}")

        return {
            'user_data': user_data,
            'oauth_token': self.access_token,
            'oauth_token_secret': self.access_token_secret
        }