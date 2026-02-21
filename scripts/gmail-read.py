#!/usr/bin/env python3
"""
Gmail readonly reader for Rudro.
Usage:
  python3 gmail-read.py                  # List 10 latest inbox emails
  python3 gmail-read.py --count 20       # List 20 emails
  python3 gmail-read.py --search "job"   # Search inbox
  python3 gmail-read.py --unread         # Unread only
"""
import sys, json, argparse
sys.path.insert(0, '/Users/mahatabrashid/Library/Python/3.9/lib/python/site-packages')

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import warnings
warnings.filterwarnings('ignore')

TOKEN_PATH = '/Users/mahatabrashid/.clawdbot/gmail/token.json'

def get_service():
    with open(TOKEN_PATH) as f:
        data = json.load(f)
    creds = Credentials(
        token=data['token'],
        refresh_token=data['refresh_token'],
        token_uri=data['token_uri'],
        client_id=data['client_id'],
        client_secret=data['client_secret'],
        scopes=data['scopes']
    )
    if creds.expired:
        creds.refresh(Request())
        # Save refreshed token
        data['token'] = creds.token
        with open(TOKEN_PATH, 'w') as f:
            json.dump(data, f, indent=2)
    return build('gmail', 'v1', credentials=creds)

def list_emails(count=10, unread_only=False, search=None):
    service = get_service()
    query = 'in:inbox'
    if unread_only:
        query += ' is:unread'
    if search:
        query += f' {search}'
    
    results = service.users().messages().list(
        userId='me', maxResults=count, q=query
    ).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print("No messages found.")
        return
    
    print(f"{'#':<4} {'FROM':<35} {'SUBJECT':<55} {'DATE':<20}")
    print("-" * 116)
    for i, msg in enumerate(messages, 1):
        m = service.users().messages().get(
            userId='me', id=msg['id'], format='metadata',
            metadataHeaders=['From', 'Subject', 'Date']
        ).execute()
        headers = {h['name']: h['value'] for h in m['payload']['headers']}
        subject = headers.get('Subject', '(no subject)')[:54]
        sender = headers.get('From', '?')[:34]
        date = headers.get('Date', '')[:19]
        unread = '★' if 'UNREAD' in m.get('labelIds', []) else ' '
        print(f"{unread}{i:<3} {sender:<35} {subject:<55} {date:<20}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=10)
    parser.add_argument('--unread', action='store_true')
    parser.add_argument('--search', type=str)
    args = parser.parse_args()
    list_emails(count=args.count, unread_only=args.unread, search=args.search)
