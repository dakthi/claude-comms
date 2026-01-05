# COMMS TOOLKIT

Power-user utilities for managing email and cloud storage across Gmail, Google Drive, and OneDrive using official APIs.

Built for AI-assisted workflows.


## FOR COMPLETE BEGINNERS

If you have never coded before, follow these steps first.

### Step 1: Install Python

Python is the programming language these tools are written in.

- Mac: Open Terminal (search "Terminal" in Spotlight), then type:

      xcode-select --install

  Then install Python from https://www.python.org/downloads/

- Windows: Download Python from https://www.python.org/downloads/
  During installation, CHECK the box that says "Add Python to PATH"

If stuck, ask ChatGPT: "How do I install Python on [Mac/Windows]?"

### Step 2: Install a Code Editor (Optional)

You can use any text editor, but Visual Studio Code is recommended.

- Download from https://code.visualstudio.com/
- Install it like any other app

If stuck, ask ChatGPT: "How do I install Visual Studio Code?"

### Step 3: Open Terminal or Command Prompt

- Mac: Search "Terminal" in Spotlight (Cmd + Space)
- Windows: Search "Command Prompt" or "PowerShell" in Start menu

This is where you type commands.

### Step 4: Download This Toolkit

In Terminal or Command Prompt, type:

    git clone https://github.com/dakthi/claude-comms.git
    cd claude-comms

If "git" is not found:
- Mac: It will prompt you to install. Say yes.
- Windows: Download from https://git-scm.com/downloads

If stuck, ask ChatGPT: "How do I clone a git repository?"

### Step 5: Install Required Packages

In Terminal, type:

    pip3 install google-api-python-client google-auth-oauthlib google-auth-httplib2 requests python-dotenv

If "pip3" is not found, try "pip" instead.

### Step 6: Set Up API Access

This requires creating accounts and getting credentials. Follow the QUICK START section below.

If any step is confusing, copy the error message and ask ChatGPT to explain.


## OVERVIEW

This toolkit provides Python scripts for:

- Gmail: inbox triage, labeling, archiving, drafting replies
- Google Drive: file organization, cross-account transfers, folder management
- OneDrive: file listing, searching, organization

All tools use official APIs with OAuth 2.0 authentication. No third-party services required.


## QUICK START

### 1. Clone and Setup

    git clone https://github.com/YOUR_USERNAME/comms-toolkit.git
    cd comms-toolkit

    pip3 install google-api-python-client google-auth-oauthlib google-auth-httplib2 requests python-dotenv

### 2. Get API Credentials

GOOGLE (GMAIL + DRIVE):

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a project
3. Enable Gmail API and Google Drive API
4. Create OAuth 2.0 Client ID (Desktop app)
5. Download credentials.json to .secrets/

MICROSOFT (ONEDRIVE):

1. Go to Azure Portal: https://portal.azure.com/
2. Register an app in Azure AD
3. Add Files.ReadWrite and User.Read permissions
4. Copy Client ID to .secrets/.env:

    ONEDRIVE_CLIENT_ID=your-client-id-here

### 3. Authenticate

    python3 gmail_tool.py auth
    python3 onedrive_tool.py auth


## FILE STRUCTURE

    comms/
    |-- README.md              Main documentation
    |-- gmail_tool.py          Gmail and Google Drive API tool
    |-- onedrive_tool.py       OneDrive API tool
    |-- .gitignore             Excludes secrets and personal data
    |-- .secrets/              (gitignored) Your credentials
    |   |-- credentials.json   Google OAuth client
    |   |-- token.json         Google access token
    |   |-- onedrive_token.json
    |   +-- .env               OneDrive client ID
    +-- logs/                  (gitignored) Session logs
        +-- CLEANUP-YYYY-MM-DD.md


## GMAIL TOOL

### CLI Commands

    python3 gmail_tool.py inbox 20          View inbox
    python3 gmail_tool.py unread            View unread
    python3 gmail_tool.py search "query"    Search
    python3 gmail_tool.py read MSG_ID       Read message
    python3 gmail_tool.py labels            List labels
    python3 gmail_tool.py unsub "email"     Trash all from sender
    python3 gmail_tool.py mark-all-read     Mark all as read

### Drive Commands

    python3 gmail_tool.py drive             List recent files
    python3 gmail_tool.py drive-folders     List folders
    python3 gmail_tool.py drive-search "x"  Search files

### Python API

    from gmail_tool import *

    # List messages
    msgs = list_messages('in:inbox is:unread', 50)

    # Get message details
    msg = get_message(msg_id)
    # Returns: id, from, to, subject, date, snippet, body, labels

    # Label and archive
    label_and_archive('from:newsletter.com in:inbox', 'Notifications/Newsletters', 50)

    # Switch accounts
    set_account('personal')
    set_account('work')


## ONEDRIVE TOOL

### CLI Commands

    python3 onedrive_tool.py auth           Authenticate
    python3 onedrive_tool.py me             Show user info
    python3 onedrive_tool.py ls             List root
    python3 onedrive_tool.py ls Documents   List folder
    python3 onedrive_tool.py folders        List all folders
    python3 onedrive_tool.py search "name"  Search files
    python3 onedrive_tool.py mkdir "name"   Create folder

### Python API

    from onedrive_tool import *

    files = list_files('Documents', 50)
    folders = list_root_folders()
    results = search_files('report', 20)
    create_folder('New Folder', parent_path='Documents')


## DRIVE ORGANIZATION WORKFLOW

### Step 1: Audit Current State

    folders = list_root_folders()
    files_at_root = list_drive_files("'root' in parents", 100)

### Step 2: Create Type-Based Folders

    _Documents/
    _Spreadsheets/
    _PDFs/
    _Images/
    _Videos/
    _Other/
    _Books/

### Step 3: Move Loose Files

    drive.files().update(
        fileId=file_id,
        addParents=folder_id,
        removeParents='root'
    ).execute()

### Step 4: Create Content-Based Folders

    Business/
    |-- Project A/
    |-- Project B/
    +-- Clients/

    Personal/
    |-- Finance/
    |-- Health/
    +-- Travel/

### Step 5: Cross-Account Transfers

To move files between Google accounts:

    # 1. Share from source account
    source_drive.permissions().create(
        fileId=folder_id,
        body={'type': 'user', 'role': 'writer', 'emailAddress': 'dest@gmail.com'},
        sendNotificationEmail=False
    ).execute()

    # 2. Switch to destination account and copy
    set_account('destination')
    dest_drive = get_drive_service()

    # 3. Recursively copy
    def copy_folder(source_id, parent_id, name):
        new_folder = dest_drive.files().create(body={
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }).execute()

        items = source_drive.files().list(
            q=f"'{source_id}' in parents"
        ).execute().get('files', [])

        for item in items:
            if 'folder' in item['mimeType']:
                copy_folder(item['id'], new_folder['id'], item['name'])
            else:
                dest_drive.files().copy(
                    fileId=item['id'],
                    body={'name': item['name'], 'parents': [new_folder['id']]}
                ).execute()


## GMAIL ORGANIZATION WORKFLOW

### Step 1: Analyze Inbox

    python3 gmail_tool.py senders 100

### Step 2: Create Label Hierarchy

    Receipts/
    |-- Food
    |-- Transport
    |-- Shopping
    +-- Subscriptions

    Notifications/
    |-- Dev
    |-- Finance
    |-- Social
    +-- Promotions

    Personal/
    |-- Friends
    |-- Family
    +-- Health

    Business/
    |-- Clients
    |-- Leads
    +-- Admin

### Step 3: Batch Label and Archive

    while True:
        count = label_and_archive('from:github.com in:inbox', 'Notifications/Dev', 50)
        if count == 0:
            break

### Step 4: Trash Marketing Spam

    python3 gmail_tool.py unsub "spam@newsletter.com"


## MULTI-ACCOUNT SETUP

Add credentials for each account:

    .secrets/
    |-- credentials.json           Account 1 (personal)
    |-- token.json
    |-- work_credentials.json      Account 2 (work)
    +-- work_token.json

In gmail_tool.py, accounts are configured as:

    ACCOUNTS = {
        'personal': {
            'credentials': SECRETS_DIR / 'credentials.json',
            'token': SECRETS_DIR / 'token.json'
        },
        'work': {
            'credentials': SECRETS_DIR / 'work_credentials.json',
            'token': SECRETS_DIR / 'work_token.json'
        }
    }

Switch accounts with:

    set_account('work')


## AI ASSISTANT INTEGRATION

This toolkit is designed to work with AI assistants like Claude Code.

### Reading Before Drafting

Important: Always read the FULL email thread before drafting replies. Initial emails often lack complete context.

    for msg_id in ['id1', 'id2', 'id3']:
        msg = get_message(msg_id)
        print(f"{msg['date']}: {msg['body']}")

### Creating Thread Replies

    orig = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    thread_id = orig['threadId']
    headers = {h['name']: h['value'] for h in orig['payload']['headers']}

    message['In-Reply-To'] = headers.get('Message-ID')
    message['References'] = headers.get('Message-ID')

    draft = service.users().drafts().create(
        userId='me',
        body={'message': {'raw': raw, 'threadId': thread_id}}
    ).execute()

### Batch Operations Safety

- Always use batches of 50 or less
- Add delays between batches to avoid rate limits
- Test with narrow queries first


## TROUBLESHOOTING

TOKEN EXPIRED:

    rm .secrets/token.json
    python3 gmail_tool.py auth

SCOPE CHANGES:

If you add new API scopes, delete the token and re-auth.

RATE LIMITS:

If you hit userRateLimitExceeded, wait 60 seconds, reduce batch size, or add time.sleep(1) between operations.

ONEDRIVE AUTH ISSUES:

    rm .secrets/onedrive_token.json
    python3 onedrive_tool.py auth


## SECURITY NOTES

- Never commit credentials. All secrets are gitignored.
- Use test users. Google OAuth apps in testing mode need explicit test users.
- Review before running. Always preview queries before batch operations.
- Backup first. Use Google Takeout before major cleanups.


## DEPENDENCIES

    pip3 install google-api-python-client google-auth-oauthlib google-auth-httplib2 requests python-dotenv


## LICENSE

MIT License. Use freely, modify as needed.


## CONTRIBUTING

1. Fork the repo
2. Create your feature branch
3. Commit changes
4. Push to the branch
5. Open a Pull Request

Keep credentials out of commits. Add any new secret files to .gitignore.
