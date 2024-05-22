## Configuration:

FACEBOOK_APP_ID and FACEBOOK_APP_SECRET: Your Facebook App credentials.
REDIRECT_URI: The URI to redirect the user after authorization.
SCOPES: Permissions requested from Facebook (read_orders in this case).
BASE_URL: Base URL for the Facebook Graph API.
API_VERSION: Facebook Graph API version used.

## Flask App:

app: Flask application instance.
secret_key: Secret key for session management.
SESSION_TYPE: Configures session storage to use the filesystem.
AUTHLIB_INSECURE_TRANSPORT: Allows insecure transport for development (not recommended for production).

## OAuth Configuration:

oauth: OAuth object for managing OAuth communication.
facebook: OAuth remote app for Facebook configured with credentials, request parameters, URLs, etc.

## Routes:

/: Renders a welcome message.
/login: Initiates OAuth login flow with Facebook.
/logout: Clears the Facebook access token from the session and redirects to the home page.
/login/authorized: Handles the callback after Facebook authorization and retrieves the access token.
/extract-data: Extracts Facebook Ads campaign data (GET or POST request).

## Functions:

authenticate_facebook: Retrieves the ad account ID associated with the access token.
fetch_campaign_data: Fetches campaign data for a specific date range and ad account.
extract_data: Handles data extraction logic, including retrieving access token, fetching data, and saving it to a JSON file.
Running the Application:

