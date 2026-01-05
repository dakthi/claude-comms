#!/usr/bin/env python3
"""
Gmail Tool - Using Google's Official API
"""

import os
import json
import base64
from datetime import datetime
from pathlib import Path

# AI API imports (optional)
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
]

CONFIG_DIR = Path(__file__).parent
SECRETS_DIR = CONFIG_DIR / '.secrets'
CREDENTIALS_FILE = SECRETS_DIR / 'credentials.json'
TOKEN_FILE = SECRETS_DIR / 'token.json'

# Thielts account credentials
THIELTS_CREDENTIALS_FILE = SECRETS_DIR / 'thielts_credentials.json'
THIELTS_TOKEN_FILE = SECRETS_DIR / 'thielts_token.json'

# Current account selector
_current_account = 'personal'  # 'personal' or 'thielts'


def set_account(account):
    """Switch between 'personal' and 'thielts' accounts."""
    global _current_account
    _current_account = account
    print(f"Switched to {account} account")


def get_credentials():
    """Get authenticated credentials for current account."""
    global _current_account

    if _current_account == 'thielts':
        creds_file = THIELTS_CREDENTIALS_FILE
        token_file = THIELTS_TOKEN_FILE
    else:
        creds_file = CREDENTIALS_FILE
        token_file = TOKEN_FILE

    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
    return creds


def get_service():
    """Authenticate and return Gmail service."""
    return build('gmail', 'v1', credentials=get_credentials())


def get_drive_service():
    """Authenticate and return Drive service."""
    return build('drive', 'v3', credentials=get_credentials())


def list_messages(query='', max_results=10):
    """List messages matching query."""
    service = get_service()
    results = service.users().messages().list(
        userId='me', q=query, maxResults=max_results
    ).execute()
    return results.get('messages', [])


def get_message(msg_id):
    """Get full message details."""
    service = get_service()
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    headers = {h['name']: h['value'] for h in msg['payload']['headers']}

    body = ''
    payload = msg['payload']
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
    elif 'body' in payload and payload['body'].get('data'):
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    return {
        'id': msg_id,
        'from': headers.get('From', ''),
        'to': headers.get('To', ''),
        'subject': headers.get('Subject', ''),
        'date': headers.get('Date', ''),
        'snippet': msg.get('snippet', ''),
        'body': body[:2000] if body else msg.get('snippet', ''),
        'labels': msg.get('labelIds', [])
    }


def trash_message(msg_id):
    """Move message to trash."""
    service = get_service()
    service.users().messages().trash(userId='me', id=msg_id).execute()
    return True


def mark_read(msg_id):
    """Mark message as read."""
    service = get_service()
    service.users().messages().modify(
        userId='me', id=msg_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()
    return True


def mark_all_read(query='is:unread'):
    """Mark all matching messages as read."""
    messages = list_messages(query, max_results=100)
    service = get_service()
    count = 0
    for msg in messages:
        service.users().messages().modify(
            userId='me', id=msg['id'],
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        count += 1
    return count


def trash_spam():
    """Move all spam to trash."""
    messages = list_messages('in:spam', max_results=500)
    service = get_service()
    count = 0
    for msg in messages:
        service.users().messages().trash(userId='me', id=msg['id']).execute()
        count += 1
    return count


def unsubscribe_sender(email):
    """Trash all emails from a sender."""
    messages = list_messages(f'from:{email}', max_results=500)
    service = get_service()
    count = 0
    for msg in messages:
        service.users().messages().trash(userId='me', id=msg['id']).execute()
        count += 1
    return count


def get_labels():
    """List all labels."""
    service = get_service()
    results = service.users().labels().list(userId='me').execute()
    return results.get('labels', [])


def create_label(name):
    """Create a new label."""
    service = get_service()
    label = {'name': name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
    result = service.users().labels().create(userId='me', body=label).execute()
    return result['id']


def get_or_create_label(name):
    """Get label ID or create if doesn't exist."""
    labels = get_labels()
    for label in labels:
        if label['name'] == name:
            return label['id']
    return create_label(name)


def archive_message(msg_id):
    """Archive message (remove from inbox)."""
    service = get_service()
    service.users().messages().modify(
        userId='me', id=msg_id,
        body={'removeLabelIds': ['INBOX']}
    ).execute()
    return True


def label_and_archive(query, label_name, max_results=50):
    """Label messages and archive them."""
    messages = list_messages(query, max_results=max_results)
    if not messages:
        return 0

    label_id = get_or_create_label(label_name)
    service = get_service()
    count = 0

    for msg in messages:
        service.users().messages().modify(
            userId='me', id=msg['id'],
            body={'addLabelIds': [label_id], 'removeLabelIds': ['INBOX', 'UNREAD']}
        ).execute()
        count += 1

    return count


def get_senders_summary(query='in:inbox', max_check=200):
    """Get summary of senders (for cleanup)."""
    messages = list_messages(query, max_results=max_check)
    senders = {}
    for msg in messages:
        details = get_message(msg['id'])
        sender = details['from']
        if sender not in senders:
            senders[sender] = 0
        senders[sender] += 1
    # Sort by count
    return sorted(senders.items(), key=lambda x: x[1], reverse=True)


def download_attachments(msg_id, save_dir='.'):
    """Download all attachments from a message."""
    import os
    service = get_service()
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()

    parts = msg['payload'].get('parts', [])
    downloaded = []

    for part in parts:
        if part.get('filename') and part['filename']:
            filename = part['filename']
            att_id = part['body'].get('attachmentId')
            if att_id:
                att = service.users().messages().attachments().get(
                    userId='me', messageId=msg_id, id=att_id
                ).execute()
                data = base64.urlsafe_b64decode(att['data'])
                filepath = os.path.join(save_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(data)
                downloaded.append(filepath)

    return downloaded


def save_email(msg_id, save_path):
    """Save email as .eml file."""
    service = get_service()
    msg = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
    raw = base64.urlsafe_b64decode(msg['raw'])
    with open(save_path, 'wb') as f:
        f.write(raw)
    return save_path


def save_email_html(msg_id, save_path):
    """Save email as HTML file for printing."""
    service = get_service()
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    headers = {h['name']: h['value'] for h in msg['payload']['headers']}

    # Get HTML body
    body_html = ''
    payload = msg['payload']

    def find_html(part):
        if part.get('mimeType') == 'text/html':
            data = part['body'].get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
        if 'parts' in part:
            for p in part['parts']:
                result = find_html(p)
                if result:
                    return result
        return None

    body_html = find_html(payload)

    if not body_html:
        # Fallback to plain text
        body_text = get_message(msg_id)['body']
        body_html = f'<pre>{body_text}</pre>'

    html = f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{headers.get('Subject', 'Email')}</title></head>
<body>
<div style="font-family: Arial; max-width: 800px; margin: auto; padding: 20px;">
<p><strong>From:</strong> {headers.get('From', '')}</p>
<p><strong>To:</strong> {headers.get('To', '')}</p>
<p><strong>Date:</strong> {headers.get('Date', '')}</p>
<p><strong>Subject:</strong> {headers.get('Subject', '')}</p>
<hr>
{body_html}
</div>
</body>
</html>'''

    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return save_path


# ============== Export Functions ==============

COMMS_DIR = Path.home() / 'Documents' / 'Factory-Tech' / 'comms'

def export_emails(query, folder_name, max_results=50):
    """Export emails matching query to local folder as HTML."""
    import re
    service = get_service()

    # Create folder if needed
    folder = COMMS_DIR / folder_name
    folder.mkdir(parents=True, exist_ok=True)

    messages = list_messages(query, max_results)
    exported = 0

    for msg in messages:
        details = get_message(msg['id'])

        # Create safe filename from date and subject
        date_str = details['date'][:16].replace(':', '-').replace(' ', '_').replace(',', '')
        subject = re.sub(r'[^\w\s-]', '', details['subject'])[:50].strip()
        filename = f"{date_str}_{subject}.html"
        filepath = folder / filename

        # Save as HTML
        save_email_html(msg['id'], str(filepath))
        exported += 1

        # Also download attachments
        atts = download_attachments(msg['id'], str(folder))

    return exported


def export_label(label_name, max_results=100):
    """Export all emails with a label to local folder."""
    # Map label to folder
    folder_map = {
        'Business': 'business',
        'Personal': 'personal',
        'Receipts': 'receipts',
        'Notifications': 'notifications',
        '100 rejections': 'jobs/rejections',
        "You're great!!": 'personal/compliments',
    }

    # Find folder for this label
    folder = None
    for prefix, path in folder_map.items():
        if label_name.startswith(prefix):
            folder = path
            break

    if not folder:
        folder = label_name.lower().replace('/', '_')

    return export_emails(f'label:{label_name}', folder, max_results)


# ============== Drive Functions ==============

def list_drive_files(query='', max_results=20):
    """List files in Drive."""
    drive = get_drive_service()
    results = drive.files().list(
        q=query,
        pageSize=max_results,
        fields='files(id, name, mimeType, modifiedTime, size, parents)'
    ).execute()
    return results.get('files', [])


def get_drive_file(file_id):
    """Get file metadata."""
    drive = get_drive_service()
    return drive.files().get(fileId=file_id, fields='*').execute()


def list_drive_folders():
    """List all folders."""
    return list_drive_files("mimeType='application/vnd.google-apps.folder'", 100)


def search_drive(name):
    """Search files by name."""
    return list_drive_files(f"name contains '{name}'", 50)


def create_drive_folder(name, parent_id=None):
    """Create a folder in Drive."""
    drive = get_drive_service()
    metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        metadata['parents'] = [parent_id]
    folder = drive.files().create(body=metadata, fields='id, name').execute()
    return folder


def get_or_create_drive_folder(name, parent_id=None):
    """Get folder by name or create if doesn't exist."""
    drive = get_drive_service()
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    else:
        query += " and 'root' in parents"

    results = drive.files().list(q=query, fields='files(id, name)').execute()
    files = results.get('files', [])

    if files:
        return files[0]
    return create_drive_folder(name, parent_id)


def move_drive_file(file_id, new_parent_id):
    """Move a file/folder to a new parent folder."""
    drive = get_drive_service()
    # Get current parents
    file = drive.files().get(fileId=file_id, fields='parents').execute()
    previous_parents = ','.join(file.get('parents', []))

    # Move to new parent
    drive.files().update(
        fileId=file_id,
        addParents=new_parent_id,
        removeParents=previous_parents,
        fields='id, name, parents'
    ).execute()
    return True


def list_root_folders():
    """List all folders at root level."""
    drive = get_drive_service()
    results = drive.files().list(
        q="'root' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
        pageSize=100,
        fields='files(id, name, mimeType)'
    ).execute()
    return results.get('files', [])


def download_drive_file(file_id, save_path):
    """Download a file from Drive."""
    import io
    from googleapiclient.http import MediaIoBaseDownload

    drive = get_drive_service()

    # Get file metadata
    file_meta = drive.files().get(fileId=file_id, fields='name, mimeType').execute()

    # For Google Docs, export as PDF
    if 'google-apps' in file_meta.get('mimeType', ''):
        request = drive.files().export_media(fileId=file_id, mimeType='application/pdf')
    else:
        request = drive.files().get_media(fileId=file_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    with open(save_path, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())

    return save_path


def list_folder_contents(folder_id):
    """List all files in a folder."""
    drive = get_drive_service()
    results = drive.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        pageSize=100,
        fields='files(id, name, mimeType, modifiedTime, size)'
    ).execute()
    return results.get('files', [])


def get_docs_service():
    """Authenticate and return Docs service."""
    return build('docs', 'v1', credentials=get_credentials())


def create_google_doc(title, content='', folder_id=None):
    """Create a Google Doc with content."""
    drive = get_drive_service()
    docs = get_docs_service()

    # Create empty doc
    metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.document'}
    if folder_id:
        metadata['parents'] = [folder_id]

    doc_file = drive.files().create(body=metadata, fields='id').execute()
    doc_id = doc_file['id']

    # Add content if provided
    if content:
        requests = [{'insertText': {'location': {'index': 1}, 'text': content}}]
        docs.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

    return {'id': doc_id, 'url': f'https://docs.google.com/document/d/{doc_id}/edit'}


def update_google_doc(doc_id, content):
    """Replace content in a Google Doc."""
    docs = get_docs_service()

    # Get current doc to find end index
    doc = docs.documents().get(documentId=doc_id).execute()
    end_index = doc['body']['content'][-1]['endIndex'] - 1

    requests = []
    # Delete existing content (if any)
    if end_index > 1:
        requests.append({'deleteContentRange': {'range': {'startIndex': 1, 'endIndex': end_index}}})
    # Insert new content
    requests.append({'insertText': {'location': {'index': 1}, 'text': content}})

    docs.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    return True


# ============== Print Functions ==============

def print_messages(messages, show_body=False):
    """Print messages in readable format."""
    if not messages:
        print("No messages found.")
        return
    for msg in messages:
        details = get_message(msg['id'])
        print(f"\n{'='*60}")
        print(f"ID: {details['id']}")
        print(f"From: {details['from']}")
        print(f"Subject: {details['subject']}")
        print(f"Date: {details['date']}")
        if show_body:
            print(f"\n{details['body'][:500]}...")
        else:
            print(f"Preview: {details['snippet'][:100]}...")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("""
Gmail Tool - Commands:

  READING:
    inbox [n]              - Show inbox (default 10)
    unread [n]             - Show unread messages
    search "query"         - Search emails
    read <id>              - Read full message
    labels                 - List all labels
    senders [n]            - Show top senders (for cleanup)

  CLEANUP:
    trash-spam             - Move all spam to trash
    trash <id>             - Move message to trash
    mark-read <id>         - Mark as read
    mark-all-read          - Mark all unread as read
    unsub "email"          - Trash all from sender

  DOWNLOAD/SAVE:
    download <id> [dir]    - Download attachments to dir
    save <id> [path]       - Save email as .eml file
    save-html <id> [path]  - Save email as HTML (for printing)

  DRIVE:
    drive                  - List recent Drive files
    drive-folders          - List all folders
    drive-search "name"    - Search files by name

  AUTH:
    auth                   - Authenticate (first time)
        """)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == 'auth':
        print("Authenticating...")
        get_service()
        print("✓ Authentication successful!")

    elif cmd == 'inbox':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print_messages(list_messages('in:inbox', n))

    elif cmd == 'unread':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print_messages(list_messages('is:unread', n))

    elif cmd == 'search':
        query = sys.argv[2] if len(sys.argv) > 2 else ''
        print_messages(list_messages(query, 20))

    elif cmd == 'read':
        msg_id = sys.argv[2]
        d = get_message(msg_id)
        print(f"\nFrom: {d['from']}")
        print(f"To: {d['to']}")
        print(f"Subject: {d['subject']}")
        print(f"Date: {d['date']}")
        print(f"\n{d['body']}")

    elif cmd == 'labels':
        for label in get_labels():
            print(f"  {label['name']}")

    elif cmd == 'senders':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        print("\nTop senders in inbox:")
        for sender, count in get_senders_summary('in:inbox', n)[:20]:
            print(f"  {count:3d} - {sender[:60]}")

    elif cmd == 'trash-spam':
        count = trash_spam()
        print(f"✓ Moved {count} spam messages to trash")

    elif cmd == 'trash':
        msg_id = sys.argv[2]
        trash_message(msg_id)
        print(f"✓ Moved to trash")

    elif cmd == 'mark-read':
        msg_id = sys.argv[2]
        mark_read(msg_id)
        print(f"✓ Marked as read")

    elif cmd == 'mark-all-read':
        count = mark_all_read()
        print(f"✓ Marked {count} messages as read")

    elif cmd == 'unsub':
        email = sys.argv[2]
        count = unsubscribe_sender(email)
        print(f"✓ Trashed {count} emails from {email}")

    elif cmd == 'download':
        msg_id = sys.argv[2]
        save_dir = sys.argv[3] if len(sys.argv) > 3 else '.'
        files = download_attachments(msg_id, save_dir)
        if files:
            print(f"✓ Downloaded {len(files)} attachments:")
            for f in files:
                print(f"  {f}")
        else:
            print("No attachments found")

    elif cmd == 'save':
        msg_id = sys.argv[2]
        save_path = sys.argv[3] if len(sys.argv) > 3 else f'{msg_id}.eml'
        save_email(msg_id, save_path)
        print(f"✓ Saved to {save_path}")

    elif cmd == 'save-html':
        msg_id = sys.argv[2]
        save_path = sys.argv[3] if len(sys.argv) > 3 else f'{msg_id}.html'
        save_email_html(msg_id, save_path)
        print(f"✓ Saved HTML to {save_path}")

    elif cmd == 'drive':
        files = list_drive_files('', 20)
        print(f"\nRecent Drive files ({len(files)}):")
        for f in files:
            size = f.get('size', 'folder')
            print(f"  {f['name'][:50]:50} {size:>10}")

    elif cmd == 'drive-folders':
        folders = list_drive_folders()
        print(f"\nDrive folders ({len(folders)}):")
        for f in folders:
            print(f"  {f['name']}")

    elif cmd == 'drive-search':
        query = sys.argv[2] if len(sys.argv) > 2 else ''
        files = search_drive(query)
        print(f"\nSearch results for '{query}' ({len(files)}):")
        for f in files:
            print(f"  {f['name']}")

    else:
        print(f"Unknown command: {cmd}")
