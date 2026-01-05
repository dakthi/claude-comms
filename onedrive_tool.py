#!/usr/bin/env python3
"""
OneDrive Tool - Using Microsoft Graph API (Personal Accounts)
Uses device code flow - no app registration needed
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

CONFIG_DIR = Path(__file__).parent
SECRETS_DIR = CONFIG_DIR / '.secrets'

# Load environment variables
load_dotenv(SECRETS_DIR / '.env')

CLIENT_ID = os.getenv('ONEDRIVE_CLIENT_ID')
SCOPES = ["Files.ReadWrite", "User.Read", "offline_access"]
ONEDRIVE_TOKEN_FILE = SECRETS_DIR / 'onedrive_token.json'

_token = None


def get_token():
    """Get access token, refreshing if needed."""
    global _token

    if ONEDRIVE_TOKEN_FILE.exists():
        with open(ONEDRIVE_TOKEN_FILE) as f:
            _token = json.load(f)

        # Try to refresh if we have refresh token
        if 'refresh_token' in _token:
            refreshed = refresh_token(_token['refresh_token'])
            if refreshed:
                return _token['access_token']

    # Need new auth
    return device_code_auth()


def device_code_auth():
    """Authenticate using device code flow."""
    global _token
    import time

    if not CLIENT_ID:
        print("Error: ONEDRIVE_CLIENT_ID not set in .env")
        return None

    # Request device code
    try:
        response = requests.post(
            "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode",
            data={
                "client_id": CLIENT_ID,
                "scope": " ".join(SCOPES)
            },
            timeout=30
        )
    except requests.RequestException as e:
        print(f"Network error: {e}")
        return None

    if response.status_code != 200:
        print(f"Error requesting device code: {response.text}")
        return None

    data = response.json()

    print("\n" + "="*50)
    print("To sign in, use a web browser to open:")
    print(f"  {data['verification_uri']}")
    print(f"\nAnd enter the code: {data['user_code']}")
    print("="*50)
    print("Waiting for authentication... (timeout: 5 min)\n")

    # Poll for token with timeout
    interval = data.get('interval', 5)
    expires_in = data.get('expires_in', 300)
    start_time = time.time()

    while time.time() - start_time < expires_in:
        time.sleep(interval)

        try:
            token_response = requests.post(
                "https://login.microsoftonline.com/consumers/oauth2/v2.0/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "client_id": CLIENT_ID,
                    "device_code": data['device_code']
                },
                timeout=30
            )
        except requests.RequestException as e:
            print(f"Network error during polling: {e}")
            continue

        token_data = token_response.json()

        if 'access_token' in token_data:
            _token = token_data
            # Ensure secrets dir exists
            SECRETS_DIR.mkdir(exist_ok=True)
            # Save token
            with open(ONEDRIVE_TOKEN_FILE, 'w') as f:
                json.dump(_token, f)
            print("✓ Authentication successful!")
            return _token['access_token']

        if token_data.get('error') == 'authorization_pending':
            print(".", end="", flush=True)
            continue
        elif token_data.get('error') == 'slow_down':
            interval += 5
            continue
        else:
            print(f"\nError: {token_data.get('error_description', token_data)}")
            return None

    print("\nAuthentication timed out. Please try again.")
    return None


def refresh_token(refresh_token_str):
    """Refresh the access token."""
    global _token

    try:
        response = requests.post(
            "https://login.microsoftonline.com/consumers/oauth2/v2.0/token",
            data={
                "grant_type": "refresh_token",
                "client_id": CLIENT_ID,
                "refresh_token": refresh_token_str,
                "scope": " ".join(SCOPES)
            },
            timeout=30
        )
    except requests.RequestException as e:
        print(f"Network error refreshing token: {e}")
        return False

    if response.status_code == 200:
        _token = response.json()
        SECRETS_DIR.mkdir(exist_ok=True)
        with open(ONEDRIVE_TOKEN_FILE, 'w') as f:
            json.dump(_token, f)
        return True

    # Refresh failed - token may be revoked
    print(f"Token refresh failed: {response.text}")
    return False


def api_request(endpoint, method='GET', **kwargs):
    """Make an authenticated API request."""
    global _token

    token = get_token()
    if not token:
        return None

    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0{endpoint}"

    response = requests.request(method, url, headers=headers, **kwargs)

    if response.status_code == 401:
        # Token expired, re-auth
        _token = None
        if ONEDRIVE_TOKEN_FILE.exists():
            ONEDRIVE_TOKEN_FILE.unlink()
        token = get_token()
        if not token:
            return None
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.request(method, url, headers=headers, **kwargs)

    return response.json() if response.status_code in [200, 201] else None


# ============== OneDrive Functions ==============

def get_user():
    """Get current user info."""
    return api_request("/me")


def list_files(folder_path="root", max_results=50):
    """List files in a folder."""
    if folder_path == "root":
        endpoint = f"/me/drive/root/children?$top={max_results}"
    else:
        endpoint = f"/me/drive/root:/{folder_path}:/children?$top={max_results}"

    result = api_request(endpoint)
    return result.get('value', []) if result else []


def search_files(query, max_results=50):
    """Search files by name."""
    endpoint = f"/me/drive/root/search(q='{query}')?$top={max_results}"
    result = api_request(endpoint)
    return result.get('value', []) if result else []


def get_file(file_id):
    """Get file metadata."""
    return api_request(f"/me/drive/items/{file_id}")


def create_folder(name, parent_path="root"):
    """Create a folder."""
    if parent_path == "root":
        endpoint = "/me/drive/root/children"
    else:
        endpoint = f"/me/drive/root:/{parent_path}:/children"

    return api_request(endpoint, method='POST', json={
        "name": name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": "rename"
    })


def move_file(file_id, new_parent_id, new_name=None):
    """Move a file to a new folder."""
    data = {"parentReference": {"id": new_parent_id}}
    if new_name:
        data["name"] = new_name

    return api_request(f"/me/drive/items/{file_id}", method='PATCH', json=data)


def rename_file(file_id, new_name):
    """Rename a file."""
    return api_request(f"/me/drive/items/{file_id}", method='PATCH', json={"name": new_name})


def delete_file(file_id):
    """Delete a file."""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}",
        headers=headers
    )
    return response.status_code == 204


def download_file(file_id, save_path):
    """Download a file."""
    # Get download URL
    file_info = api_request(f"/me/drive/items/{file_id}")
    if not file_info:
        return None

    download_url = file_info.get('@microsoft.graph.downloadUrl')
    if not download_url:
        return None

    response = requests.get(download_url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

    return save_path


def list_root_folders():
    """List all folders at root level."""
    files = list_files("root", 100)
    return [f for f in files if 'folder' in f]


def get_folder_contents(folder_id):
    """List all files in a folder by ID."""
    result = api_request(f"/me/drive/items/{folder_id}/children?$top=100")
    return result.get('value', []) if result else []


# ============== CLI ==============

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("""
OneDrive Tool - Commands:

  auth              - Authenticate (first time)
  me                - Show current user
  ls [path]         - List files (default: root)
  search "query"    - Search files
  folders           - List root folders
  mkdir "name"      - Create folder at root

Example:
  python onedrive_tool.py auth
  python onedrive_tool.py ls
  python onedrive_tool.py ls Documents
  python onedrive_tool.py search "report"
        """)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == 'auth':
        print("Authenticating...")
        device_code_auth()

    elif cmd == 'me':
        user = get_user()
        if user:
            print(f"User: {user.get('displayName')}")
            print(f"Email: {user.get('userPrincipalName')}")

    elif cmd == 'ls':
        path = sys.argv[2] if len(sys.argv) > 2 else "root"
        files = list_files(path, 30)
        print(f"\nFiles in {path}:")
        for f in files:
            ftype = "📁" if 'folder' in f else "📄"
            size = f.get('size', 0)
            print(f"  {ftype} {f['name'][:50]:50} {size:>10}")

    elif cmd == 'search':
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        files = search_files(query, 20)
        print(f"\nSearch results for '{query}':")
        for f in files:
            print(f"  {f['name']}")

    elif cmd == 'folders':
        folders = list_root_folders()
        print(f"\nRoot folders ({len(folders)}):")
        for f in folders:
            print(f"  📁 {f['name']}")

    elif cmd == 'mkdir':
        name = sys.argv[2] if len(sys.argv) > 2 else "New Folder"
        result = create_folder(name)
        if result:
            print(f"✓ Created folder: {name}")

    else:
        print(f"Unknown command: {cmd}")
