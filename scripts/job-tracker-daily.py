#!/usr/bin/env python3
"""
Job Application Tracker - Daily Scan
Scans Gmail + MSN for yesterday's job application emails.
Adds new rows and updates existing ones in the Google Sheet.
Run daily at 9 AM PST.
"""
import sys, json, os, re, base64, warnings, urllib.request, urllib.parse
from datetime import datetime, date, timedelta
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser

warnings.filterwarnings('ignore')
sys.path.insert(0, '/Users/mahatabrashid/Library/Python/3.9/lib/python/site-packages')

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ── Config ────────────────────────────────────────────────────────────────────
GMAIL_TOKEN_PATH  = os.path.expanduser('~/.clawdbot/gmail/token.json')
MSN_TOKEN_PATH    = os.path.expanduser('~/.clawdbot/msn/token.json')
MSN_CLIENT_ID     = '7ed8b008-8f80-4c57-a7be-773210b67021'
MSN_TENANT        = 'consumers'
STATE_PATH        = os.path.expanduser('~/clawd/memory/job-applications.json')
SHEET_ID_PATH     = os.path.expanduser('~/clawd/memory/job-tracker-sheet-id.txt')
TODAY             = date.today()
YESTERDAY         = TODAY - timedelta(days=1)
DATE_FROM         = YESTERDAY.strftime('%Y/%m/%d')
DATE_TO           = TODAY.strftime('%Y/%m/%d')
DATE_FROM_ISO     = YESTERDAY.strftime('%Y-%m-%dT00:00:00Z')
DATE_TO_ISO       = TODAY.strftime('%Y-%m-%dT00:00:00Z')

print(f"=== Job Tracker Daily Scan: {YESTERDAY} ===")

# ── Helpers ───────────────────────────────────────────────────────────────────
class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []; self.skip = 0
        self.skip_tags = {'script', 'style', 'head'}
    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags: self.skip += 1
    def handle_endtag(self, tag):
        if tag in self.skip_tags: self.skip = max(0, self.skip - 1)
    def handle_data(self, data):
        if self.skip == 0 and data.strip(): self.result.append(data.strip())
    def get_text(self): return ' '.join(self.result)

def decode_body(part):
    data = part.get('body', {}).get('data', '')
    return base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace') if data else ''

def extract_text(parts):
    plain, html = '', ''
    for p in parts:
        mime = p.get('mimeType', '')
        if mime == 'text/plain': plain += decode_body(p)
        elif mime == 'text/html': html += decode_body(p)
        elif mime.startswith('multipart/'):
            pl, hl = extract_text(p.get('parts', []))
            plain += pl; html += hl
    return plain, html

def html_to_text(html):
    try:
        e = HTMLTextExtractor(); e.feed(html); return e.get_text()
    except: return re.sub('<[^>]+>', ' ', html)

def get_msg_text(msg):
    payload = msg.get('payload', {})
    mime = payload.get('mimeType', '')
    plain, html = '', ''
    if mime == 'text/plain': plain = decode_body(payload)
    elif mime == 'text/html': html = decode_body(payload)
    elif mime.startswith('multipart/'): plain, html = extract_text(payload.get('parts', []))
    return plain if plain else html_to_text(html)

def get_header(msg, name):
    for h in msg.get('payload', {}).get('headers', []):
        if h['name'].lower() == name.lower(): return h['value']
    return ''

def parse_date(msg):
    ds = get_header(msg, 'Date')
    try: return parsedate_to_datetime(ds).date() if ds else None
    except: return None

FALSE_POSITIVE_DOMAINS = ['hdbfs.com','sbicard.com','jio.com','marutidealers.com',
    'starterstory.com','zintro.com','amazon.com','ebay.com','paypal.com',
    'bankofamerica.com','chase.com','netflix.com']
FALSE_POSITIVE_SUBJECTS = ['email verification','loan application','order number',
    'confirmation code','paid research','newsletter','unsubscribe','your order',
    'shipment','delivery','tracking','password reset','security alert']

def is_false_positive(sender, subject):
    sl = sender.lower(); sub = subject.lower()
    return (any(d in sl for d in FALSE_POSITIVE_DOMAINS) or
            any(s in sub for s in FALSE_POSITIVE_SUBJECTS))

PLATFORM_MAP = {
    'greenhouse.io': 'Greenhouse', 'lever.co': 'Lever',
    'workday.com': 'Workday', 'myworkdayjobs.com': 'Workday',
    'icims.com': 'iCIMS', 'smartrecruiters.com': 'SmartRecruiters',
    'taleo.net': 'Taleo', 'jobvite.com': 'Jobvite',
    'ashbyhq.com': 'Ashby', 'linkedin.com': 'LinkedIn',
}

def detect_platform(sender, text):
    sl = sender.lower()
    for domain, name in PLATFORM_MAP.items():
        if domain in sl: return name
    if 'google.com' in sl: return 'Google Careers'
    if 'microsoft.com' in sl: return 'Microsoft Careers'
    return 'Direct/Company Website'

def detect_status(subjects, text):
    combined = ' '.join(subjects).lower() + ' ' + text.lower()
    if any(k in combined for k in ['hiring assessment','interview','phone screen','next round','technical screen','next steps','schedule a call','move forward with','advance you']):
        return 'Interview Scheduled'
    if any(k in combined for k in ['not move forward','not moving forward','regret to inform','decided to pursue','not selected','unfortunately','will not be moving','decided not to']):
        return 'Rejected'
    if any(k in combined for k in ['under review','reviewing your','being considered','still being']):
        return 'Under Review'
    return 'Applied'

def extract_job_id(text):
    for pat in [
        r'(?:jobId|job_id|gh_jid|req_id|jobcode|currentJobId)=([A-Za-z0-9_\-]+)',
        r'/jobs?/([0-9]{5,15})(?:[/?#]|$)',
        r'(?:Job\s*(?:ID|#|Id)[:\s]+)([A-Za-z0-9_\-]{4,30})',
        r'linkedin\.com/jobs/view/([0-9]+)',
    ]:
        m = re.search(pat, text[:8000], re.IGNORECASE)
        if m:
            jid = m.group(1)
            if jid.lower() not in ['apply','jobs','careers','view','new','dashboard']:
                return jid
    return 'N/A'

def extract_position(text, subject):
    combined = subject + ' ' + text[:3000]
    for pat in [
        r'applied for(?: the)? ([A-Za-z][A-Za-z0-9\s\-,/&]{5,60}?)(?:\s+(?:at|position|role)|[,\.\n])',
        r'application for(?: the)? ([A-Za-z][A-Za-z0-9\s\-,/&]{5,60}?)(?:\s+position|[,\.\n])',
        r'for the ([A-Za-z][A-Za-z0-9\s\-,/&]{5,60}?) (?:role|position)',
        r'Position[:\s]+([A-Za-z][A-Za-z0-9\s\-,/&]{5,60}?)(?:[,\.\n])',
    ]:
        m = re.search(pat, combined, re.IGNORECASE)
        if m:
            pos = m.group(1).strip()
            if len(pos) > 5: return pos[:80]
    return 'Unknown Position'

# ── Load Gmail credentials ────────────────────────────────────────────────────
with open(GMAIL_TOKEN_PATH) as f: gmail_data = json.load(f)
gmail_creds = Credentials(
    token=gmail_data['token'], refresh_token=gmail_data['refresh_token'],
    token_uri=gmail_data['token_uri'], client_id=gmail_data['client_id'],
    client_secret=gmail_data['client_secret'], scopes=gmail_data['scopes']
)
if gmail_creds.expired:
    gmail_creds.refresh(Request())
    gmail_data['token'] = gmail_creds.token
    with open(GMAIL_TOKEN_PATH, 'w') as f: json.dump(gmail_data, f, indent=2)

gmail = build('gmail', 'v1', credentials=gmail_creds)
sheets = build('sheets', 'v4', credentials=gmail_creds)

# ── Load sheet info ───────────────────────────────────────────────────────────
with open(SHEET_ID_PATH) as f: SPREADSHEET_ID = f.read().strip()
sheet_meta = sheets.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
GRID_ID = sheet_meta['sheets'][0]['properties']['sheetId']
print(f"Sheet: {SPREADSHEET_ID} (gridId: {GRID_ID})")

# ── Load existing applications ────────────────────────────────────────────────
existing_apps = []
if os.path.exists(STATE_PATH):
    with open(STATE_PATH) as f:
        state = json.load(f)
    existing_apps = state.get('applications', [])
print(f"Existing applications: {len(existing_apps)}")

def find_existing(job_id, company, position, date_applied):
    """Find matching existing application."""
    for i, app in enumerate(existing_apps):
        # Primary key: job_id + company
        if job_id != 'N/A' and app.get('job_id') == job_id and app.get('company_name','').lower() == company.lower():
            return i
        # Fallback: company + position (fuzzy) + date ±3 days
        if app.get('company_name','').lower() == company.lower():
            pos_match = app.get('position_title','').lower()[:30] == position.lower()[:30]
            try:
                existing_date = datetime.strptime(app.get('date_applied','01/01/2000'), '%m/%d/%Y').date()
                date_obj = datetime.strptime(date_applied, '%m/%d/%Y').date()
                date_close = abs((existing_date - date_obj).days) <= 3
            except: date_close = False
            if pos_match and date_close:
                return i
    return -1

# ── Scan Gmail ────────────────────────────────────────────────────────────────
print(f"\n=== Scanning Gmail ({YESTERDAY}) ===")
gmail_queries = [
    f'"Thanks for applying" after:{DATE_FROM} before:{DATE_TO}',
    f'"Thank you for applying" after:{DATE_FROM} before:{DATE_TO}',
    f'"Thank you for your interest" after:{DATE_FROM} before:{DATE_TO}',
    f'"Thanks for your interest" after:{DATE_FROM} before:{DATE_TO}',
    f'"You applied for" after:{DATE_FROM} before:{DATE_TO}',
    f'"Your application was sent" after:{DATE_FROM} before:{DATE_TO}',
    f'from:greenhouse.io after:{DATE_FROM} before:{DATE_TO}',
    f'from:lever.co after:{DATE_FROM} before:{DATE_TO}',
    f'from:myworkdayjobs.com after:{DATE_FROM} before:{DATE_TO}',
    f'from:workday.com after:{DATE_FROM} before:{DATE_TO}',
    f'from:greenhouse-mail.io after:{DATE_FROM} before:{DATE_TO}',
    f'from:noreply@google.com "applying" after:{DATE_FROM} before:{DATE_TO}',
    f'(from:(career) OR from:(talent) OR from:(recruit)) ("applied" OR "application") after:{DATE_FROM} before:{DATE_TO}',
]

gmail_thread_ids = set()
for q in gmail_queries:
    r = gmail.users().threads().list(userId='me', q=q, maxResults=50).execute()
    for t in r.get('threads', []): gmail_thread_ids.add(t['id'])

print(f"Gmail threads found: {len(gmail_thread_ids)}")
new_apps, updated_apps = [], []

for tid in gmail_thread_ids:
    try:
        thread = gmail.users().threads().get(userId='me', id=tid, format='full').execute()
        msgs = sorted(thread.get('messages', []), key=lambda m: int(m.get('internalDate', 0)))
        if not msgs: continue

        first = msgs[0]
        sender = get_header(first, 'From')
        subject = get_header(first, 'Subject')
        if is_false_positive(sender, subject): continue

        all_text = '\n'.join(get_msg_text(m) for m in msgs)
        all_subjects = [get_header(m, 'Subject') for m in msgs]
        date_applied = parse_date(first)
        if not date_applied: continue
        last_update = parse_date(msgs[-1]) or date_applied

        company_m = re.search(r'@([^>@\s\.]+)', sender)
        company = company_m.group(1).title() if company_m else 'Unknown'
        position = extract_position(all_text, subject)
        job_id = extract_job_id(all_text)
        platform = detect_platform(sender, all_text)
        status = detect_status(all_subjects, all_text)
        days_since = (TODAY - date_applied).days
        follow_up = 'YES' if status in ('Applied', 'No Response') and days_since > 14 else 'NO'

        app = {
            'job_id': job_id, 'company_name': company, 'position_title': position,
            'date_applied': date_applied.strftime('%m/%d/%Y'),
            'source_platform': platform, 'email_account': 'mahatab@gmail.com',
            'current_status': status, 'last_update_date': last_update.strftime('%m/%d/%Y'),
            'follow_up_needed': follow_up, 'days_since_applied': days_since, 'notes': ''
        }

        idx = find_existing(job_id, company, position, app['date_applied'])
        if idx >= 0:
            # Update existing
            STATUS_PRIORITY = {'Interview Scheduled': 4, 'Under Review': 3, 'Rejected': 2, 'Applied': 1, 'No Response': 0}
            old = existing_apps[idx]
            if STATUS_PRIORITY.get(status, 0) > STATUS_PRIORITY.get(old.get('current_status', ''), 0):
                existing_apps[idx]['current_status'] = status
            existing_apps[idx]['last_update_date'] = last_update.strftime('%m/%d/%Y')
            existing_apps[idx]['days_since_applied'] = days_since
            existing_apps[idx]['follow_up_needed'] = follow_up
            updated_apps.append(company)
        else:
            new_apps.append(app)
            existing_apps.append(app)
            print(f"  NEW: [{date_applied}] {company} | {position[:40]} | {status}")
    except Exception as e:
        print(f"  Error processing thread {tid}: {e}")

# ── Scan MSN ──────────────────────────────────────────────────────────────────
print(f"\n=== Scanning MSN ({YESTERDAY}) ===")
with open(MSN_TOKEN_PATH) as f: msn_data = json.load(f)

def msn_refresh():
    global msn_data
    data = urllib.parse.urlencode({
        'client_id': MSN_CLIENT_ID, 'grant_type': 'refresh_token',
        'refresh_token': msn_data['refresh_token'], 'scope': 'Mail.Read offline_access'
    }).encode()
    req = urllib.request.Request(f'https://login.microsoftonline.com/{MSN_TENANT}/oauth2/v2.0/token', data=data, method='POST')
    with urllib.request.urlopen(req) as r: new_tok = json.load(r)
    msn_data.update(new_tok)
    with open(MSN_TOKEN_PATH, 'w') as f: json.dump(msn_data, f, indent=2)

def msn_get(path):
    headers = {'Authorization': f"Bearer {msn_data['access_token']}"}
    url = f'https://graph.microsoft.com/v1.0{path}'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            msn_refresh()
            headers = {'Authorization': f"Bearer {msn_data['access_token']}"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as r: return json.load(r)
        raise

msn_phrases = [
    'Thanks for applying', 'Thank you for applying',
    'Thank you for your interest', 'Thanks for your interest',
    'You applied for', 'Your application was sent', 'application received'
]

msn_msg_ids = {}
for phrase in msn_phrases:
    try:
        encoded = urllib.parse.quote(f'"{phrase}"')
        filter_q = urllib.parse.quote(f"receivedDateTime ge {DATE_FROM_ISO} and receivedDateTime le {DATE_TO_ISO}")
        path = f'/me/messages?$search={encoded}&$top=50&$select=id,subject,from,receivedDateTime,conversationId,bodyPreview&$filter={filter_q}'
        result = msn_get(path)
        for msg in result.get('value', []):
            mid = msg['id']
            if mid not in msn_msg_ids:
                msn_msg_ids[mid] = msg
    except Exception as e:
        print(f"  MSN search error for '{phrase}': {e}")

print(f"MSN messages found: {len(msn_msg_ids)}")

# Group by conversation
msn_convos = {}
for msg in msn_msg_ids.values():
    cid = msg.get('conversationId', msg['id'])
    if cid not in msn_convos: msn_convos[cid] = []
    msn_convos[cid].append(msg)

for cid, msgs in msn_convos.items():
    try:
        msgs.sort(key=lambda m: m.get('receivedDateTime', ''))
        first = msgs[0]
        sender_info = first.get('from', {}).get('emailAddress', {})
        sender = f"{sender_info.get('name','')} <{sender_info.get('address','')}>"
        subject = first.get('subject', '')

        if is_false_positive(sender, subject): continue

        all_text = ' '.join(m.get('bodyPreview', '') for m in msgs)
        all_subjects = [m.get('subject', '') for m in msgs]

        try: date_applied = datetime.fromisoformat(first['receivedDateTime'].replace('Z','+00:00')).date()
        except: continue
        try: last_update = datetime.fromisoformat(msgs[-1]['receivedDateTime'].replace('Z','+00:00')).date()
        except: last_update = date_applied

        company_m = re.search(r'<([^>@\s]+)@', sender)
        company = company_m.group(1).title() if company_m else 'Unknown'
        position = extract_position(all_text, subject)
        job_id = extract_job_id(all_text)
        platform = detect_platform(sender, all_text)
        status = detect_status(all_subjects, all_text)
        days_since = (TODAY - date_applied).days
        follow_up = 'YES' if status in ('Applied', 'No Response') and days_since > 14 else 'NO'

        app = {
            'job_id': job_id, 'company_name': company, 'position_title': position,
            'date_applied': date_applied.strftime('%m/%d/%Y'),
            'source_platform': platform, 'email_account': 'mahatab@msn.com',
            'current_status': status, 'last_update_date': last_update.strftime('%m/%d/%Y'),
            'follow_up_needed': follow_up, 'days_since_applied': days_since, 'notes': ''
        }

        idx = find_existing(job_id, company, position, app['date_applied'])
        if idx >= 0:
            STATUS_PRIORITY = {'Interview Scheduled': 4, 'Under Review': 3, 'Rejected': 2, 'Applied': 1, 'No Response': 0}
            old = existing_apps[idx]
            if STATUS_PRIORITY.get(status, 0) > STATUS_PRIORITY.get(old.get('current_status', ''), 0):
                existing_apps[idx]['current_status'] = status
            existing_apps[idx]['last_update_date'] = last_update.strftime('%m/%d/%Y')
            existing_apps[idx]['days_since_applied'] = days_since
            existing_apps[idx]['follow_up_needed'] = follow_up
            updated_apps.append(company)
        else:
            new_apps.append(app)
            existing_apps.append(app)
            print(f"  NEW: [{date_applied}] {company} | {position[:40]} | {status}")
    except Exception as e:
        print(f"  Error processing MSN convo {cid}: {e}")

# ── Re-evaluate follow-up for all Applied/No Response older than 14 days ──────
print(f"\n=== Re-evaluating Follow-Up Needed ===")
followup_updated = 0
for app in existing_apps:
    if app.get('current_status') in ('Applied', 'No Response'):
        try:
            d = datetime.strptime(app['date_applied'], '%m/%d/%Y').date()
            days = (TODAY - d).days
            app['days_since_applied'] = days
            new_fu = 'YES' if days > 14 else 'NO'
            if app.get('follow_up_needed') != new_fu:
                app['follow_up_needed'] = new_fu
                followup_updated += 1
        except: pass
print(f"Follow-up flags updated: {followup_updated}")

# ── Write to sheet ────────────────────────────────────────────────────────────
print(f"\n=== Writing to Sheet ===")
existing_apps.sort(key=lambda x: x.get('date_applied', '01/01/2000'), reverse=True)

HEADERS = ['Job ID','Company Name','Position Title','Date Applied','Source/Platform',
           'Email Account','Current Status','Last Update Date','Follow-Up Needed',
           'Days Since Applied','Notes']

rows = [HEADERS]
for app in existing_apps:
    rows.append([
        app.get('job_id','N/A'), app.get('company_name',''), app.get('position_title',''),
        app.get('date_applied',''), app.get('source_platform',''), app.get('email_account',''),
        app.get('current_status',''), app.get('last_update_date',''),
        app.get('follow_up_needed',''), app.get('days_since_applied',0), app.get('notes','')
    ])

sheets.spreadsheets().values().clear(spreadsheetId=SPREADSHEET_ID, range='Applications!A:Z').execute()
sheets.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID, range='Applications!A1',
    valueInputOption='USER_ENTERED', body={'values': rows}
).execute()

# Apply formatting
STATUS_COLORS = {
    'Rejected':            {'red': 0.878, 'green': 0.878, 'blue': 0.878},
    'Interview Scheduled': {'red': 0.784, 'green': 0.902, 'blue': 0.784},
}
FOLLOWUP_COLOR = {'red': 1.0, 'green': 0.976, 'blue': 0.769}

requests = [
    {'repeatCell': {
        'range': {'sheetId': GRID_ID, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': len(HEADERS)},
        'cell': {'userEnteredFormat': {
            'textFormat': {'bold': True, 'foregroundColor': {'red':1,'green':1,'blue':1}},
            'backgroundColor': {'red': 0.102, 'green': 0.322, 'blue': 0.478},
            'horizontalAlignment': 'CENTER'
        }},
        'fields': 'userEnteredFormat(textFormat,backgroundColor,horizontalAlignment)'
    }},
    {'updateSheetProperties': {
        'properties': {'sheetId': GRID_ID, 'gridProperties': {'frozenRowCount': 1}},
        'fields': 'gridProperties.frozenRowCount'
    }},
    {'autoResizeDimensions': {
        'dimensions': {'sheetId': GRID_ID, 'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': len(HEADERS)}
    }}
]

for i, app in enumerate(existing_apps):
    status = app.get('current_status', '')
    fu = app.get('follow_up_needed', 'NO')
    color = STATUS_COLORS.get(status, FOLLOWUP_COLOR if fu == 'YES' else None)
    if color:
        requests.append({'repeatCell': {
            'range': {'sheetId': GRID_ID, 'startRowIndex': i+1, 'endRowIndex': i+2, 'startColumnIndex': 0, 'endColumnIndex': len(HEADERS)},
            'cell': {'userEnteredFormat': {'backgroundColor': color}},
            'fields': 'userEnteredFormat(backgroundColor)'
        }})

sheets.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={'requests': requests}).execute()

# ── Save state ────────────────────────────────────────────────────────────────
status_counts = {}
for app in existing_apps:
    s = app.get('current_status', 'Unknown')
    status_counts[s] = status_counts.get(s, 0) + 1

state = {
    'sheet_id': SPREADSHEET_ID,
    'last_scan': str(TODAY),
    'scan_type': 'daily',
    'total': len(existing_apps),
    'status_counts': status_counts,
    'applications': existing_apps
}
with open(STATE_PATH, 'w') as f: json.dump(state, f, indent=2)

print(f"\n{'='*60}")
print(f"✅ Daily scan complete!")
print(f"   New applications: {len(new_apps)}")
print(f"   Updated applications: {len(updated_apps)}")
print(f"   Total in sheet: {len(existing_apps)}")
for s, c in sorted(status_counts.items(), key=lambda x: -x[1]):
    print(f"   {s}: {c}")
print(f"   Sheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
