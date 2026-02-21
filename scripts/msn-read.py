#!/usr/bin/env python3
"""
Read-only access to mahatab@msn.com via Microsoft Graph API.
Usage:
  python3 msn-read.py [--count N] [--unread] [--search "query"] [--folder FOLDER]
"""
import sys, json, os, argparse, time
import urllib.request, urllib.parse, urllib.error

TOKEN_PATH = os.path.expanduser('~/.clawdbot/msn/token.json')
CLIENT_ID = '7ed8b008-8f80-4c57-a7be-773210b67021'
TENANT = 'consumers'

def load_token():
    with open(TOKEN_PATH) as f:
        return json.load(f)

def save_token(data):
    with open(TOKEN_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def refresh_token(token_data):
    """Refresh the access token using the refresh token."""
    data = urllib.parse.urlencode({
        'client_id': CLIENT_ID,
        'grant_type': 'refresh_token',
        'refresh_token': token_data['refresh_token'],
        'scope': 'Mail.Read offline_access'
    }).encode()
    req = urllib.request.Request(
        f'https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token',
        data=data, method='POST'
    )
    with urllib.request.urlopen(req) as resp:
        result = json.load(resp)
    token_data.update(result)
    save_token(token_data)
    return token_data

def get_access_token():
    token_data = load_token()
    # Check expiry (expires_in is seconds from issue, use ext_expires_in as buffer)
    # Simple approach: try refresh if we have refresh_token
    try:
        # Test token by making a lightweight call
        headers = {'Authorization': f"Bearer {token_data['access_token']}"}
        req = urllib.request.Request(
            'https://graph.microsoft.com/v1.0/me/mailFolders/inbox?$select=id',
            headers=headers
        )
        urllib.request.urlopen(req)
        return token_data['access_token']
    except urllib.error.HTTPError as e:
        if e.code == 401 and 'refresh_token' in token_data:
            token_data = refresh_token(token_data)
            return token_data['access_token']
        raise

def graph_get(path, access_token):
    url = f'https://graph.microsoft.com/v1.0{path}'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)

def main():
    parser = argparse.ArgumentParser(description='Read mahatab@msn.com emails')
    parser.add_argument('--count', type=int, default=10, help='Number of emails to show')
    parser.add_argument('--unread', action='store_true', help='Show only unread emails')
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--folder', type=str, default='inbox', help='Folder (inbox, sentItems, etc.)')
    args = parser.parse_args()

    token = get_access_token()

    # Build query
    params = {
        '$top': args.count,
        '$select': 'subject,from,receivedDateTime,isRead,bodyPreview,hasAttachments',
        '$orderby': 'receivedDateTime desc'
    }

    filters = []
    if args.unread:
        filters.append('isRead eq false')
    if filters:
        params['$filter'] = ' and '.join(filters)

    if args.search:
        params['$search'] = f'"{args.search}"'
        params.pop('$orderby', None)  # can't use orderby with search

    query_str = '&'.join(f'{k}={urllib.parse.quote(str(v))}' for k, v in params.items())
    path = f'/me/mailFolders/{args.folder}/messages?{query_str}'

    result = graph_get(path, token)
    messages = result.get('value', [])

    print(f"\n📬 mahatab@msn.com — {args.folder} ({len(messages)} emails)\n")
    print("-" * 80)

    for msg in messages:
        date = msg.get('receivedDateTime', '')[:10]
        sender = msg.get('from', {}).get('emailAddress', {})
        subject = msg.get('subject', '(no subject)')
        is_read = msg.get('isRead', True)
        has_att = '📎' if msg.get('hasAttachments') else ''
        unread_mark = '🔵' if not is_read else '  '
        preview = msg.get('bodyPreview', '')[:100].replace('\n', ' ')

        print(f"{unread_mark} [{date}] {has_att}")
        print(f"   From: {sender.get('name', '')} <{sender.get('address', '')}>")
        print(f"   Subject: {subject}")
        print(f"   Preview: {preview}")
        print()

    print("-" * 80)
    total_unread = sum(1 for m in messages if not m.get('isRead', True))
    print(f"Showing {len(messages)} emails | {total_unread} unread in this view\n")

if __name__ == '__main__':
    main()
