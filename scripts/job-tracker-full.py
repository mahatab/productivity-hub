#!/usr/bin/env python3
"""
Job Application Tracker - Full Pipeline
Steps 1-8: Create Sheet, Scan Gmail, Scan MSN, Filter, Extract, Deduplicate, Write, Save
"""

import sys, json, warnings, os, re, base64, time
from datetime import datetime, date, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser

warnings.filterwarnings('ignore')
sys.path.insert(0, '/Users/mahatabrashid/Library/Python/3.9/lib/python/site-packages')

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import requests as req_lib

TODAY = date(2026, 2, 17)
GMAIL_TOKEN_PATH = os.path.expanduser('~/.clawdbot/gmail/token.json')
MSN_TOKEN_PATH   = os.path.expanduser('~/.clawdbot/msn/token.json')
SHEET_ID_PATH    = '/Users/mahatabrashid/clawd/memory/job-tracker-sheet-id.txt'
APPS_JSON_PATH   = '/Users/mahatabrashid/clawd/memory/job-applications.json'

# ─────────────────── CREDENTIALS ───────────────────

def get_google_creds():
    with open(GMAIL_TOKEN_PATH) as f:
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
        data['token'] = creds.token
        with open(GMAIL_TOKEN_PATH, 'w') as f:
            json.dump(data, f, indent=2)
    return creds

def get_msn_token():
    with open(MSN_TOKEN_PATH) as f:
        data = json.load(f)
    # Check if access token still valid (try it; refresh on 401)
    return data

def refresh_msn_token(token_data):
    data = {
        'client_id': '7ed8b008-8f80-4c57-a7be-773210b67021',
        'grant_type': 'refresh_token',
        'refresh_token': token_data['refresh_token'],
        'scope': 'Mail.Read offline_access'
    }
    resp = req_lib.post(
        'https://login.microsoftonline.com/consumers/oauth2/v2.0/token',
        data=data, timeout=30
    )
    if resp.status_code == 200:
        new_data = resp.json()
        token_data['access_token'] = new_data['access_token']
        if 'refresh_token' in new_data:
            token_data['refresh_token'] = new_data['refresh_token']
        with open(MSN_TOKEN_PATH, 'w') as f:
            json.dump(token_data, f, indent=2)
        print("  MSN token refreshed successfully.")
        return token_data
    else:
        print(f"  MSN token refresh failed: {resp.status_code} {resp.text[:200]}")
        return token_data

# ─────────────────── HTML / TEXT UTILS ───────────────────

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.skip_tags = {'script', 'style', 'head'}
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.skip = max(0, self.skip - 1)
    def handle_data(self, data):
        if self.skip == 0 and data.strip():
            self.result.append(data.strip())
    def get_text(self):
        return ' '.join(self.result)

def html_to_text(html):
    parser = HTMLTextExtractor()
    try:
        parser.feed(html)
        return parser.get_text()
    except:
        return re.sub('<[^>]+>', ' ', html)

def decode_b64(data):
    if not data:
        return ''
    try:
        return base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace')
    except:
        return ''

def extract_text_from_parts(parts):
    plain, html = '', ''
    for part in parts:
        mime = part.get('mimeType', '')
        if mime == 'text/plain':
            plain += decode_b64(part.get('body', {}).get('data', ''))
        elif mime == 'text/html':
            html += decode_b64(part.get('body', {}).get('data', ''))
        elif mime.startswith('multipart/'):
            p, h = extract_text_from_parts(part.get('parts', []))
            plain += p
            html += h
    return plain, html

def get_email_text(msg):
    payload = msg.get('payload', {})
    mime = payload.get('mimeType', '')
    plain, html = '', ''
    if mime == 'text/plain':
        plain = decode_b64(payload.get('body', {}).get('data', ''))
    elif mime == 'text/html':
        html = decode_b64(payload.get('body', {}).get('data', ''))
    elif mime.startswith('multipart/'):
        plain, html = extract_text_from_parts(payload.get('parts', []))
    text = plain if plain else html_to_text(html) if html else ''
    return text[:12000]

def get_header(msg, name):
    for h in msg.get('payload', {}).get('headers', []):
        if h['name'].lower() == name.lower():
            return h['value']
    return ''

def parse_email_date(msg):
    date_str = get_header(msg, 'Date')
    if date_str:
        try:
            dt = parsedate_to_datetime(date_str)
            return dt.date()
        except:
            pass
    ts = int(msg.get('internalDate', '0')) / 1000
    return datetime.fromtimestamp(ts).date()

# ─────────────────── PLATFORM / COMPANY / POSITION ───────────────────

PLATFORM_MAP = {
    'linkedin.com': 'LinkedIn',
    'greenhouse.io': 'Greenhouse',
    'greenhouse-mail.io': 'Greenhouse',
    'lever.co': 'Lever',
    'workday.com': 'Workday',
    'myworkdayjobs.com': 'Workday',
    'myworkday.com': 'Workday',
    'icims.com': 'iCIMS',
    'smartrecruiters.com': 'SmartRecruiters',
    'taleo.net': 'Taleo',
    'jobvite.com': 'Jobvite',
    'ashbyhq.com': 'Ashby',
    'successfactors.com': 'SAP SuccessFactors',
    'breezy.hr': 'Breezy',
    'bamboohr.com': 'BambooHR',
    'recruitee.com': 'Recruitee',
    'indeed.com': 'Indeed',
    'ziprecruiter.com': 'ZipRecruiter',
    'wellfound.com': 'Wellfound',
    'angel.co': 'AngelList',
    'workable.com': 'Workable',
    'jazz.co': 'JazzHR',
    'eightfold.ai': 'Eightfold',
    'paradox.ai': 'Paradox/Olivia',
    'rippling.com': 'Rippling',
    'pinpointhq.com': 'Pinpoint',
    'applytojob.com': 'ApplyToJob',
    'personio.de': 'Personio',
    'recruitcrm.io': 'RecruitCRM',
    'dice.com': 'Dice',
    'monster.com': 'Monster',
    'careerbuilder.com': 'CareerBuilder',
    'glassdoor.com': 'Glassdoor',
}

SKIP_DOMAINS = [
    'hdbfs.com', 'sbicard.com', 'jio.com', 'marutidealers.com',
    'starterstory.com', 'zintro.com',
    'hdfc', 'icici', 'axis', 'kotak', 'amazon.in', 'flipkart',
    'myntra', 'irctc', 'bookmyshow', 'maruti',
]

SKIP_SUBJECT_KEYWORDS = [
    'email verification', 'loan application', 'order number',
    'confirmation code', 'paid research', 'newsletter',
    'payment', 'transaction', 'otp', 'invoice', 'shipment',
    'delivery', 'subscription', 'password reset', 'unsubscribe',
    'promo code', 'discount', 'sale', 'insurance', 'policy',
    'emi', 'credit card', 'mutual fund',
]

NON_JOB_BODY_KEYWORDS = [
    'loan', 'emi', 'credit card', 'debit card', 'bank account',
    'order confirmed', 'order placed', 'invoice', 'payment receipt',
    'otp', 'verification code', 'subscription renewal',
    'car dealer', 'vehicle', 'mutual fund', 'insurance premium',
]

JOB_KEYWORDS = [
    'apply', 'applied', 'application', 'position', 'role', 'job',
    'career', 'hiring', 'recruit', 'candidate', 'resume', 'cv',
    'opening', 'opportunity', 'interview', 'screening', 'offer',
    'hiring team', 'talent', 'onboard', 'assessment', 'shortlist',
]

def is_job_application_email(subject, text, sender):
    combined = (subject + ' ' + text[:2000]).lower()
    sender_lower = sender.lower()

    for d in SKIP_DOMAINS:
        if d in sender_lower:
            return False

    for kw in SKIP_SUBJECT_KEYWORDS:
        if kw in subject.lower():
            return False

    non_job = sum(1 for kw in NON_JOB_BODY_KEYWORDS if kw in combined)
    if non_job >= 2:
        return False

    job_count = sum(1 for kw in JOB_KEYWORDS if kw in combined)
    if job_count == 0:
        return False

    return True

def detect_platform(sender, text):
    s = sender.lower()
    t = text[:3000].lower()
    for domain, platform in PLATFORM_MAP.items():
        if domain in s:
            return platform
    # Special: Google Careers
    if 'google.com' in s or 'google.com/careers' in t:
        return 'Google Careers'
    if 'careers.microsoft.com' in t or 'microsoft.com' in s:
        return 'Microsoft Careers'
    for domain, platform in PLATFORM_MAP.items():
        if domain in t:
            return platform
    return 'Direct/Company Website'

def extract_company(sender, subject, text):
    # 1. Sender display name
    m = re.match(r'^"?([^"<@\n]{2,60}?)"?\s*<', sender)
    if m:
        display = m.group(1).strip()
        skip = ['noreply', 'no-reply', 'notification', 'team', 'recruiting',
                'careers', 'info', 'jobs', 'talent', 'hr', 'donotreply',
                'apply', 'hiring', 'support', 'hello', 'mahatab']
        if not any(s in display.lower() for s in skip):
            if not re.match(r'^[\w\.\-]+@', display) and len(display) > 2:
                return display.strip(' "').title()

    # 2. From domain (if not a known platform)
    m = re.search(r'@([^>@\s]+)', sender)
    if m:
        domain = m.group(1).lower()
        is_platform = any(p in domain for p in list(PLATFORM_MAP.keys()) + [
            'gmail', 'yahoo', 'outlook', 'hotmail', 'google', 'microsoft',
        ])
        if not is_platform:
            parts = domain.split('.')
            if len(parts) >= 2:
                company = parts[-2]
                company = re.sub(r'[-_]', ' ', company).title()
                skip_words = ['mail', 'email', 'noreply', 'no', 'info', 'jobs',
                              'careers', 'recruiting', 'talent', 'hr', 'notifications',
                              'notification', 'donotreply', 'apply', 'hello']
                if company.lower() not in skip_words and len(company) > 2:
                    return company

    # 3. Body text
    body_patterns = [
        r'(?:Thank you for applying to|applied to|application to|position at|role at|joining|welcome to|at)\s+([A-Z][A-Za-z0-9\s&\-\.\']{2,40}?)(?:\s*[,\.\n!]|\s+team|\s+for|\s+is|\s+\()',
        r'(?:from|at|with)\s+([A-Z][A-Za-z0-9\s&\-\.]{2,40}?)\s+(?:Recruiting|Talent|HR|Careers|Team)',
        r'the\s+([A-Z][A-Za-z0-9\s&\-]{3,40}?)\s+(?:team|recruiting|talent)',
    ]
    for pat in body_patterns:
        m = re.search(pat, text[:5000])
        if m:
            company = m.group(1).strip().rstrip(' ,-.')
            if len(company) > 2 and company.lower() not in ['the', 'we', 'our', 'you', 'your', 'this', 'a']:
                return company

    # 4. Subject
    for pat in [
        r'(?:application|applying|applied)[:\s]+(?:to|at|with|for)\s+([A-Z][A-Za-z0-9\s&\-]{2,40}?)(?:\s*[-–@\(\s]|$)',
        r'(?:from|at)\s+([A-Z][A-Za-z0-9\s&\-]{2,40}?)(?:\s*[-–]|\s+is|\s+has|$)',
    ]:
        m = re.search(pat, subject, re.IGNORECASE)
        if m:
            company = m.group(1).strip()
            if len(company) > 2:
                return company

    return 'Unknown'

def extract_position(subject, text):
    patterns = [
        r'(?:applied for|application for|applying for|you applied to|you applied for)[:\s]+(?:the\s+)?(?:role of\s+|position of\s+)?(?:a\s+|an\s+)?([A-Za-z][A-Za-z0-9\s\-,/&\(\)\.]{5,80}?)(?:\s+(?:at|with|position|role)|[-–@\(,\.\n]|$)',
        r'(?:role|position|job title|job opening|opening)[:\s]+([A-Za-z][A-Za-z0-9\s\-,/&\(\)]{5,60}?)(?:\s+at|\s+\(|[,\.\n]|$)',
        r'(?:Thank you for applying to|applying for)\s+(?:the\s+)?([A-Za-z][A-Za-z0-9\s\-,/&]{5,60}?)(?:\s+(?:at|with|position|role)|[,\.\n]|$)',
        r'(?:Position|Job Title|Title)[:\s]+([A-Za-z][A-Za-z0-9\s\-,/&\(\)]{5,60}?)(?:[,\.\n]|$)',
    ]
    for pat in patterns:
        m = re.search(pat, subject, re.IGNORECASE)
        if m:
            pos = m.group(1).strip().rstrip(' -–,.')
            if len(pos) > 3:
                return pos[:100]
    for pat in patterns:
        m = re.search(pat, text[:6000], re.IGNORECASE)
        if m:
            pos = m.group(1).strip().rstrip(' -–,.')
            if len(pos) > 3:
                return pos[:100]

    # Fallback from subject
    subj = re.sub(r'^(?:re:|fw:|fwd:)\s*', '', subject, flags=re.IGNORECASE).strip()
    subj = re.sub(r'(?:application|confirmation|received|submitted|thank you|applying|applied|your|we)[^-–]*$', '', subj, flags=re.IGNORECASE).strip()
    subj = subj.rstrip(' -–@|').strip()
    if subj and len(subj) > 5:
        return subj[:100]
    return 'Unknown Position'

def extract_job_id(text):
    patterns = [
        r'(?:jobId|job_id|job-id|gh_jid|jid|req_id|reqId|req-id|requisition[_-]?id|jobReqId|jobcode|jobCode|jobref|jobRef|currentJobId)=([A-Za-z0-9_\-]{4,30})',
        r'/jobs?/([A-Za-z0-9_\-]{5,30})(?:[/?#]|$)',
        r'/positions?/([A-Za-z0-9_\-]{4,30})(?:[/?#]|$)',
        r'(?:Job\s*(?:ID|#|Number|Req)[:\s#]+)([A-Za-z0-9_\-]{4,30})',
        r'(?:Req(?:uisition)?\s*(?:ID|#|Number)[:\s#]+)([A-Za-z0-9_\-]{4,30})',
        r'linkedin\.com/jobs/view/(\d{7,12})',
    ]
    for pat in patterns:
        m = re.search(pat, text[:12000], re.IGNORECASE)
        if m:
            jid = m.group(1)
            bad = {'apply', 'jobs', 'careers', 'view', 'edit', 'new', 'create',
                   'open', 'list', 'search', 'home', 'index', 'apply', 'post'}
            if len(jid) >= 4 and jid.lower() not in bad:
                return jid
    return 'N/A'

def determine_status(msgs, email_account='gmail'):
    combined = ''
    for msg in msgs:
        if email_account == 'msn':
            subject = msg.get('subject', '')
            body = msg.get('body_text', '')
        else:
            subject = get_header(msg, 'Subject')
            body = get_email_text(msg)
        combined = (subject + ' ' + body + '\n' + combined).lower()

    INTERVIEW_PATTERNS = [
        'phone interview', 'video interview', 'virtual interview',
        'interview scheduled', 'interview invitation', 'interview request',
        'phone screen', 'technical screen', 'technical interview',
        'hiring assessment', 'hiring manager', 'schedule a call',
        'we would like to invite you', "we'd like to invite you",
        'next round', 'move you forward', 'move you to the next',
        'assessment link', 'coding challenge', 'take-home assignment',
        'hackerrank', 'codility', 'pymetrics',
        'next steps', 'technical screen',
    ]
    REJECTION_PATTERNS = [
        'not moving forward', 'not selected', 'decided to move forward with other',
        'decided to pursue other candidates', 'will not be moving',
        'regret to inform', 'not a fit', 'not the right fit',
        'position has been filled', 'will not be proceeding',
        'decided to go with', 'decided not to move',
        'after careful consideration, we have decided',
        "we've decided to move forward with another",
        "we won't be moving", 'cannot move forward',
        'not be moving forward', 'we are not able to move',
        "unfortunately, we", "we have decided not",
    ]
    REVIEW_PATTERNS = [
        'under review', 'reviewing your application', 'being reviewed',
        'in review', 'actively screening', 'shortlisting',
        'will be in touch', 'keep you updated', 'being considered',
    ]

    for p in INTERVIEW_PATTERNS:
        if p in combined:
            return 'Interview Scheduled'
    for p in REJECTION_PATTERNS:
        if re.search(p, combined):
            return 'Rejected'
    for p in REVIEW_PATTERNS:
        if p in combined:
            return 'Under Review'
    return 'Applied'

def extract_notes(text, sender):
    parts = []
    url_m = re.search(
        r'https?://[^\s<>"]{10,200}(?:job|career|position|apply|req|opening)[^\s<>"]{0,150}',
        text, re.IGNORECASE
    )
    if url_m:
        parts.append(f"URL: {url_m.group(0).rstrip('.,)')[:200]}")

    for pat in [
        r'(?:Location|Office|City|Based in)[:\s]+([A-Za-z\s,]{5,50}?)(?:\n|\.|$)',
        r'\b(Remote|Hybrid|On-site|Onsite|In-office)\b',
    ]:
        m = re.search(pat, text[:4000], re.IGNORECASE)
        if m:
            loc = m.group(1).strip() if m.lastindex else m.group(0)
            parts.append(f"Location: {loc[:60]}")
            break

    salary_m = re.search(r'\$[\d,]+(?:\s*[-–to]+\s*\$[\d,]+)?(?:\s*(?:k|K|per year|\/yr|annually))?', text)
    if salary_m:
        parts.append(f"Salary: {salary_m.group(0)}")

    recruiter_m = re.search(
        r'(?:Best|Thanks|Regards|Sincerely)[,\s]+([A-Z][a-z]+ [A-Z][a-z]+)[\s\n]',
        text[:5000]
    )
    if recruiter_m:
        parts.append(f"Recruiter: {recruiter_m.group(1)}")

    return ' | '.join(parts)[:500]

# ─────────────────── STEP 1: CREATE SHEET ───────────────────

def create_sheet(sheets_service):
    body = {
        'properties': {'title': 'Mahatab - Job Applications Tracker'},
        'sheets': [{
            'properties': {
                'title': 'Applications',
                'gridProperties': {'rowCount': 2000, 'columnCount': 11}
            }
        }]
    }
    ss = sheets_service.spreadsheets().create(body=body).execute()
    spreadsheet_id = ss['spreadsheetId']
    sheet_gid = ss['sheets'][0]['properties']['sheetId']
    print(f"  Created new spreadsheet: {spreadsheet_id}")
    return spreadsheet_id, sheet_gid

def setup_sheet_headers_and_formatting(sheets_service, spreadsheet_id, sheet_gid):
    """Write headers and apply all formatting."""
    headers = [[
        'Job ID', 'Company Name', 'Position Title',
        'Date Applied (MM/DD/YYYY)', 'Source/Platform', 'Email Account',
        'Current Status', 'Last Update Date', 'Follow-Up Needed',
        'Days Since Applied', 'Notes'
    ]]
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range='Applications!A1:K1',
        valueInputOption='RAW',
        body={'values': headers}
    ).execute()

    dark_blue = {'red': 26/255, 'green': 82/255, 'blue': 118/255}   # #1a5276
    white     = {'red': 1.0, 'green': 1.0, 'blue': 1.0}
    yellow    = {'red': 1.0, 'green': 0.976, 'blue': 0.769}          # #FFF9C4
    gray      = {'red': 0.878, 'green': 0.878, 'blue': 0.878}        # #E0E0E0
    green     = {'red': 0.784, 'green': 0.902, 'blue': 0.788}        # #C8E6C9

    reqs = [
        # Freeze header row
        {'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_gid,
                'gridProperties': {'frozenRowCount': 1}
            },
            'fields': 'gridProperties.frozenRowCount'
        }},
        # Header: bold, white text, dark blue bg
        {'repeatCell': {
            'range': {'sheetId': sheet_gid, 'startRowIndex': 0, 'endRowIndex': 1,
                      'startColumnIndex': 0, 'endColumnIndex': 11},
            'cell': {'userEnteredFormat': {
                'backgroundColor': dark_blue,
                'textFormat': {'bold': True, 'foregroundColor': white, 'fontSize': 11},
                'horizontalAlignment': 'CENTER',
                'verticalAlignment': 'MIDDLE'
            }},
            'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
        }},
        # Auto-resize columns
        {'autoResizeDimensions': {
            'dimensions': {'sheetId': sheet_gid, 'dimension': 'COLUMNS',
                           'startIndex': 0, 'endIndex': 11}
        }},
        # Conditional: Follow-Up Needed (col I = col 9) = YES → yellow
        {'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_gid, 'startRowIndex': 1, 'endRowIndex': 2000,
                             'startColumnIndex': 0, 'endColumnIndex': 11}],
                'booleanRule': {
                    'condition': {'type': 'CUSTOM_FORMULA',
                                  'values': [{'userEnteredValue': '=$I2="YES"'}]},
                    'format': {'backgroundColor': yellow}
                }
            }, 'index': 0
        }},
        # Conditional: Rejected (col G = col 7) → gray
        {'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_gid, 'startRowIndex': 1, 'endRowIndex': 2000,
                             'startColumnIndex': 0, 'endColumnIndex': 11}],
                'booleanRule': {
                    'condition': {'type': 'CUSTOM_FORMULA',
                                  'values': [{'userEnteredValue': '=$G2="Rejected"'}]},
                    'format': {'backgroundColor': gray}
                }
            }, 'index': 1
        }},
        # Conditional: Interview Scheduled → green
        {'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_gid, 'startRowIndex': 1, 'endRowIndex': 2000,
                             'startColumnIndex': 0, 'endColumnIndex': 11}],
                'booleanRule': {
                    'condition': {'type': 'CUSTOM_FORMULA',
                                  'values': [{'userEnteredValue': '=$G2="Interview Scheduled"'}]},
                    'format': {'backgroundColor': green}
                }
            }, 'index': 2
        }},
    ]
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={'requests': reqs}
    ).execute()
    print("  Sheet headers and formatting applied.")

# ─────────────────── STEP 2: SCAN GMAIL ───────────────────

GMAIL_QUERIES = [
    '"Thanks for applying" after:2025/11/01 before:2026/02/18',
    '"Thank you for applying" after:2025/11/01 before:2026/02/18',
    '"Thank you for your interest" after:2025/11/01 before:2026/02/18',
    '"Thanks for your interest" after:2025/11/01 before:2026/02/18',
    'from:noreply@google.com after:2025/11/01 before:2026/02/18',
    'from:(no-reply@us.greenhouse-mail.io) after:2025/11/01 before:2026/02/18',
    'from:(career) after:2025/11/01 before:2026/02/18',
    'from:(noreply) after:2025/11/01 before:2026/02/18',
    'from:(no-reply) after:2025/11/01 before:2026/02/18',
    'from:(job) after:2025/11/01 before:2026/02/18',
    'from:(hire) after:2025/11/01 before:2026/02/18',
    'from:(talent) after:2025/11/01 before:2026/02/18',
    'from:(recruit) after:2025/11/01 before:2026/02/18',
    '"You applied for" after:2025/11/01 before:2026/02/18',
    '"Your application was sent" after:2025/11/01 before:2026/02/18',
    'from:myworkdayjobs.com after:2025/11/01 before:2026/02/18',
    'from:workday.com after:2025/11/01 before:2026/02/18',
    'from:greenhouse.io after:2025/11/01 before:2026/02/18',
    'from:lever.co after:2025/11/01 before:2026/02/18',
    'from:icims.com after:2025/11/01 before:2026/02/18',
    'from:smartrecruiters.com after:2025/11/01 before:2026/02/18',
    'from:taleo.net after:2025/11/01 before:2026/02/18',
    'from:jobvite.com after:2025/11/01 before:2026/02/18',
    'from:ashbyhq.com after:2025/11/01 before:2026/02/18',
    # Supplemental
    '"application confirmation" after:2025/11/01 before:2026/02/18',
    '"we received your application" after:2025/11/01 before:2026/02/18',
    '"application submitted" after:2025/11/01 before:2026/02/18',
    '"not moving forward" after:2025/11/01 before:2026/02/18',
    '"interview invitation" after:2025/11/01 before:2026/02/18',
    '"thank you for your application" after:2025/11/01 before:2026/02/18',
]

def gmail_search(gmail_svc, query):
    msgs, page_token = [], None
    while True:
        kwargs = {'userId': 'me', 'q': query, 'maxResults': 100}
        if page_token:
            kwargs['pageToken'] = page_token
        result = gmail_svc.users().messages().list(**kwargs).execute()
        msgs.extend(result.get('messages', []))
        page_token = result.get('nextPageToken')
        if not page_token:
            break
    return msgs

def scan_gmail(gmail_svc):
    print("\n=== STEP 2: Scanning Gmail ===")
    all_ids = set()
    for q in GMAIL_QUERIES:
        try:
            msgs = gmail_search(gmail_svc, q)
            ids = {m['id'] for m in msgs}
            if ids:
                print(f"  [{len(ids):3d}] {q[:80]}")
            all_ids.update(ids)
        except Exception as e:
            print(f"  ERROR on query '{q[:60]}': {e}")

    print(f"\n  Total unique message IDs: {len(all_ids)}")

    # Fetch full messages and group by thread
    thread_msgs = {}
    msg_list = list(all_ids)
    print(f"  Fetching {len(msg_list)} messages...")

    for i, mid in enumerate(msg_list):
        if i % 20 == 0 and i > 0:
            print(f"    {i}/{len(msg_list)}...")
        try:
            msg = gmail_svc.users().messages().get(
                userId='me', id=mid, format='full'
            ).execute()
            tid = msg.get('threadId', mid)
            thread_msgs.setdefault(tid, []).append(msg)
        except Exception as e:
            print(f"  Warning: {mid}: {e}")

    # Fetch any remaining thread messages we may have missed
    print(f"  Fetching complete threads for {len(thread_msgs)} threads...")
    complete_threads = {}
    for tid in list(thread_msgs.keys()):
        try:
            thread = gmail_svc.users().threads().get(
                userId='me', id=tid, format='full'
            ).execute()
            complete_threads[tid] = thread.get('messages', thread_msgs[tid])
        except:
            complete_threads[tid] = thread_msgs[tid]

    print(f"  Processing {len(complete_threads)} threads...")
    applications = []
    filtered_count = 0

    for tid, msgs in complete_threads.items():
        msgs.sort(key=lambda m: parse_email_date(m))
        first_msg, last_msg = msgs[0], msgs[-1]
        subject = get_header(first_msg, 'Subject')
        sender  = get_header(first_msg, 'From')
        date_applied     = parse_email_date(first_msg)
        last_update_date = parse_email_date(last_msg)

        all_text = '\n'.join(get_email_text(m) for m in msgs)

        if not is_job_application_email(subject, all_text, sender):
            filtered_count += 1
            continue

        platform = detect_platform(sender, all_text)
        company  = extract_company(sender, subject, all_text)
        position = extract_position(subject, all_text)
        job_id   = extract_job_id(all_text)
        status   = determine_status(msgs, 'gmail')

        days_since = (TODAY - date_applied).days
        follow_up  = 'YES' if status in ('Applied', 'No Response') and days_since > 14 else 'NO'
        notes      = extract_notes(all_text, sender)

        applications.append({
            'job_id':       job_id,
            'company':      company,
            'position':     position,
            'date_applied': date_applied.strftime('%m/%d/%Y'),
            'date_applied_raw': date_applied,
            'platform':     platform,
            'email_account': 'mahatab@gmail.com',
            'status':       status,
            'last_update':  last_update_date.strftime('%m/%d/%Y'),
            'follow_up':    follow_up,
            'days_since':   days_since,
            'notes':        notes,
            'thread_id':    tid,
            'source':       'gmail',
        })

    print(f"  Filtered out {filtered_count} non-job emails.")
    print(f"  Extracted {len(applications)} Gmail applications.")
    return applications

# ─────────────────── STEP 3: SCAN MSN ───────────────────

MSN_SEARCH_QUERIES = [
    "Thanks for applying",
    "Thank you for applying",
    "Thank you for your interest",
    "Thanks for your interest",
    "You applied for",
    "Your application was sent",
    "application confirmation",
    "we received your application",
    "not moving forward",
    "interview invitation",
    "thank you for your application",
    "application submitted",
]

def msn_get(url, access_token, params=None):
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    r = req_lib.get(url, headers=headers, params=params, timeout=30)
    return r

def scan_msn(token_data):
    print("\n=== STEP 3: Scanning MSN/Outlook ===")
    access_token = token_data.get('access_token', '')
    base = 'https://graph.microsoft.com/v1.0'

    # Test token
    test = msn_get(f'{base}/me', access_token)
    if test.status_code == 401:
        print("  Token expired, refreshing...")
        token_data = refresh_msn_token(token_data)
        access_token = token_data.get('access_token', '')

    seen_ids = set()
    all_msn_msgs = []

    for query in MSN_SEARCH_QUERIES:
        try:
            url = f'{base}/me/messages'
            params = {
                '$search': f'"{query}"',
                '$top': 50,
                '$select': 'id,subject,from,receivedDateTime,body,internetMessageId,conversationId',
            }
            r = msn_get(url, access_token, params=params)
            if r.status_code == 401:
                token_data = refresh_msn_token(token_data)
                access_token = token_data.get('access_token', '')
                r = msn_get(url, access_token, params=params)
            if r.status_code != 200:
                print(f"  MSN search '{query}': HTTP {r.status_code}")
                continue
            data = r.json()
            msgs = data.get('value', [])
            new_count = 0
            for msg in msgs:
                mid = msg.get('id', '')
                if mid and mid not in seen_ids:
                    # Date filter
                    recv = msg.get('receivedDateTime', '')
                    if recv:
                        try:
                            msg_date = datetime.fromisoformat(recv.replace('Z', '+00:00')).date()
                            if not (date(2025, 11, 1) <= msg_date <= date(2026, 2, 18)):
                                continue
                        except:
                            pass
                    seen_ids.add(mid)
                    all_msn_msgs.append(msg)
                    new_count += 1
            if new_count:
                print(f"  [{new_count:3d}] {query}")
        except Exception as e:
            print(f"  MSN error on '{query}': {e}")

    print(f"  Total unique MSN messages: {len(all_msn_msgs)}")

    # Group by conversationId
    convs = {}
    for msg in all_msn_msgs:
        cid = msg.get('conversationId') or msg.get('id')
        convs.setdefault(cid, []).append(msg)

    print(f"  Processing {len(convs)} MSN conversations...")
    applications = []
    filtered_count = 0

    for cid, msgs in convs.items():
        # Sort by date
        def parse_msn_date(m):
            s = m.get('receivedDateTime', '')
            try:
                return datetime.fromisoformat(s.replace('Z', '+00:00')).date()
            except:
                return TODAY
        msgs.sort(key=parse_msn_date)
        first_msg, last_msg = msgs[0], msgs[-1]

        subject = first_msg.get('subject', '')
        sender_obj = first_msg.get('from', {}).get('emailAddress', {})
        sender = f"{sender_obj.get('name','')} <{sender_obj.get('address','')}>"
        sender_addr = sender_obj.get('address', '')

        date_applied     = parse_msn_date(first_msg)
        last_update_date = parse_msn_date(last_msg)

        # Extract body text from all msgs
        all_text = ''
        for m in msgs:
            body = m.get('body', {})
            content = body.get('content', '')
            ct = body.get('contentType', 'text')
            if ct == 'html':
                all_text += html_to_text(content) + '\n'
            else:
                all_text += content + '\n'
            m['body_text'] = html_to_text(content) if ct == 'html' else content

        all_text = all_text[:12000]

        if not is_job_application_email(subject, all_text, sender_addr):
            filtered_count += 1
            continue

        platform = detect_platform(sender_addr, all_text)
        company  = extract_company(sender, subject, all_text)
        position = extract_position(subject, all_text)
        job_id   = extract_job_id(all_text)
        status   = determine_status(msgs, 'msn')

        days_since = (TODAY - date_applied).days
        follow_up  = 'YES' if status in ('Applied', 'No Response') and days_since > 14 else 'NO'
        notes      = extract_notes(all_text, sender_addr)

        applications.append({
            'job_id':       job_id,
            'company':      company,
            'position':     position,
            'date_applied': date_applied.strftime('%m/%d/%Y'),
            'date_applied_raw': date_applied,
            'platform':     platform,
            'email_account': 'mahatab@msn.com',
            'status':       status,
            'last_update':  last_update_date.strftime('%m/%d/%Y'),
            'follow_up':    follow_up,
            'days_since':   days_since,
            'notes':        notes,
            'thread_id':    cid,
            'source':       'msn',
        })

    print(f"  Filtered out {filtered_count} non-job MSN emails.")
    print(f"  Extracted {len(applications)} MSN applications.")
    return applications

# ─────────────────── STEP 6: DEDUPLICATION ───────────────────

STATUS_PRIORITY = {'Interview Scheduled': 4, 'Under Review': 3, 'Rejected': 2, 'Applied': 1}

def deduplicate(apps):
    print(f"\n=== STEP 6: Deduplication ({len(apps)} total) ===")
    deduped = {}

    for app in apps:
        job_id  = app['job_id']
        company = app['company'].lower().strip()
        pos     = app['position'].lower().strip()[:30]
        raw_date = app['date_applied_raw']

        if job_id != 'N/A':
            key = f"{job_id}|{company}"
        else:
            key = f"{company}|{pos}|{raw_date.strftime('%Y-%m-%d')}"

        if key in deduped:
            existing = deduped[key]
            # Keep highest status
            if STATUS_PRIORITY.get(app['status'], 0) > STATUS_PRIORITY.get(existing['status'], 0):
                existing['status'] = app['status']
            # Keep earliest date applied
            if app['date_applied_raw'] < existing['date_applied_raw']:
                existing['date_applied'] = app['date_applied']
                existing['date_applied_raw'] = app['date_applied_raw']
            # Keep latest update
            if app['last_update'] > existing['last_update']:
                existing['last_update'] = app['last_update']
            # Note both accounts
            if app['email_account'] != existing['email_account']:
                existing['email_account'] = existing['email_account'] + ' + ' + app['email_account']
            # Merge notes
            if app['notes'] and app['notes'] not in existing.get('notes', ''):
                existing['notes'] = (existing.get('notes', '') + ' | ' + app['notes'])[:500]
        else:
            deduped[key] = dict(app)

    result = list(deduped.values())

    # Also do fuzzy dedup for same company+role within ±3 days (for N/A job IDs)
    final = []
    used = set()
    for i, a in enumerate(result):
        if i in used:
            continue
        for j, b in enumerate(result):
            if j <= i or j in used:
                continue
            if a['job_id'] != 'N/A' or b['job_id'] != 'N/A':
                continue
            same_co  = a['company'].lower() == b['company'].lower()
            same_pos = a['position'].lower()[:20] == b['position'].lower()[:20]
            date_diff = abs((a['date_applied_raw'] - b['date_applied_raw']).days)
            if same_co and same_pos and date_diff <= 3:
                used.add(j)
                # Merge b into a
                if STATUS_PRIORITY.get(b['status'], 0) > STATUS_PRIORITY.get(a['status'], 0):
                    a['status'] = b['status']
                if b['date_applied_raw'] < a['date_applied_raw']:
                    a['date_applied'] = b['date_applied']
                    a['date_applied_raw'] = b['date_applied_raw']
                if b['last_update'] > a['last_update']:
                    a['last_update'] = b['last_update']
        final.append(a)

    # Recompute follow_up after status may have changed
    for app in final:
        days_since = (TODAY - app['date_applied_raw']).days
        app['days_since'] = days_since
        app['follow_up'] = 'YES' if app['status'] in ('Applied', 'No Response') and days_since > 14 else 'NO'

    final.sort(key=lambda x: x['date_applied_raw'], reverse=True)
    print(f"  After deduplication: {len(final)} unique applications")

    status_counts = {}
    for a in final:
        status_counts[a['status']] = status_counts.get(a['status'], 0) + 1
    print("  Status breakdown:", status_counts)

    return final, status_counts

# ─────────────────── STEP 7: WRITE TO SHEET ───────────────────

def apply_row_color(sheets_service, spreadsheet_id, sheet_gid, row_idx, status, follow_up):
    """Apply direct row background color (overrides conditional formatting for clarity)."""
    yellow = {'red': 1.0, 'green': 0.976, 'blue': 0.769}
    gray   = {'red': 0.878, 'green': 0.878, 'blue': 0.878}
    green  = {'red': 0.784, 'green': 0.902, 'blue': 0.788}
    white  = {'red': 1.0, 'green': 1.0, 'blue': 1.0}

    if status == 'Interview Scheduled':
        color = green
    elif status == 'Rejected':
        color = gray
    elif follow_up == 'YES':
        color = yellow
    else:
        color = white

    return {
        'repeatCell': {
            'range': {'sheetId': sheet_gid,
                      'startRowIndex': row_idx, 'endRowIndex': row_idx + 1,
                      'startColumnIndex': 0, 'endColumnIndex': 11},
            'cell': {'userEnteredFormat': {'backgroundColor': color}},
            'fields': 'userEnteredFormat.backgroundColor'
        }
    }

def write_to_sheet(sheets_service, spreadsheet_id, applications):
    print(f"\n=== STEP 7: Writing {len(applications)} rows to sheet ===")

    # Get sheet gid
    ss = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_gid = ss['sheets'][0]['properties']['sheetId']

    # Clear existing data (keep header)
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range='Applications!A2:K2000'
    ).execute()

    # Prepare rows
    rows = []
    for app in applications:
        rows.append([
            app['job_id'],
            app['company'],
            app['position'],
            app['date_applied'],
            app['platform'],
            app['email_account'],
            app['status'],
            app['last_update'],
            app['follow_up'],
            app['days_since'],
            app['notes'],
        ])

    if rows:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f'Applications!A2:K{1+len(rows)}',
            valueInputOption='RAW',
            body={'values': rows}
        ).execute()

    # Apply row colors (batch)
    color_requests = []
    for i, app in enumerate(applications):
        row_idx = i + 1  # 0-indexed, row 0 is header
        color_requests.append(apply_row_color(
            sheets_service, spreadsheet_id, sheet_gid,
            row_idx, app['status'], app['follow_up']
        ))

    if color_requests:
        # Batch in chunks of 100
        for chunk_start in range(0, len(color_requests), 100):
            chunk = color_requests[chunk_start:chunk_start+100]
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body={'requests': chunk}
            ).execute()

    # Auto-resize after data write
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': [{'autoResizeDimensions': {
            'dimensions': {'sheetId': sheet_gid, 'dimension': 'COLUMNS',
                           'startIndex': 0, 'endIndex': 11}
        }}]}
    ).execute()

    print(f"  Wrote {len(rows)} rows to sheet.")
    print(f"  Sheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")

# ─────────────────── STEP 8: SAVE STATE ───────────────────

def save_state(spreadsheet_id, applications, status_counts):
    # Strip non-serializable fields
    clean = []
    for app in applications:
        a = dict(app)
        a.pop('date_applied_raw', None)
        a.pop('thread_id', None)
        a.pop('source', None)
        clean.append(a)

    state = {
        'sheet_id':   spreadsheet_id,
        'last_scan':  '2026-02-17',
        'scan_type':  'historical',
        'total':      len(clean),
        'status_counts': status_counts,
        'applications': clean,
    }

    with open(APPS_JSON_PATH, 'w') as f:
        json.dump(state, f, indent=2)
    print(f"\n  Saved state to {APPS_JSON_PATH}")

# ─────────────────── MAIN ───────────────────

def main():
    print("=" * 70)
    print("JOB APPLICATION TRACKER - FULL PIPELINE")
    print("=" * 70)

    # ── Credentials ──
    print("\nLoading credentials...")
    creds = get_google_creds()
    sheets_service = build('sheets', 'v4', credentials=creds)
    gmail_svc      = build('gmail',  'v1', credentials=creds)
    msn_token      = get_msn_token()

    # ── STEP 1: Sheet ──
    print("\n=== STEP 1: Google Sheet ===")
    existing_id = None
    try:
        with open(SHEET_ID_PATH) as f:
            existing_id = f.read().strip()
        print(f"  Found existing sheet ID: {existing_id}")
        # Verify it exists
        ss_info = sheets_service.spreadsheets().get(spreadsheetId=existing_id).execute()
        # Check for correct sheet name and columns
        sheets_list = ss_info.get('sheets', [])
        apps_sheet = next((s for s in sheets_list if s['properties']['title'] == 'Applications'), None)
        if apps_sheet:
            # Check if Email Account column exists (should have 11 columns)
            sheet_gid = apps_sheet['properties']['sheetId']
            vals = sheets_service.spreadsheets().values().get(
                spreadsheetId=existing_id, range='Applications!A1:K1'
            ).execute().get('values', [[]])
            if vals and len(vals[0]) >= 11 and vals[0][5] == 'Email Account':
                print(f"  Reusing existing sheet (correct columns confirmed).")
                spreadsheet_id = existing_id
            else:
                print(f"  Existing sheet has wrong columns. Creating new sheet...")
                spreadsheet_id, sheet_gid = create_sheet(sheets_service)
                setup_sheet_headers_and_formatting(sheets_service, spreadsheet_id, sheet_gid)
                with open(SHEET_ID_PATH, 'w') as f:
                    f.write(spreadsheet_id)
        else:
            print(f"  No 'Applications' tab. Re-creating...")
            spreadsheet_id, sheet_gid = create_sheet(sheets_service)
            setup_sheet_headers_and_formatting(sheets_service, spreadsheet_id, sheet_gid)
            with open(SHEET_ID_PATH, 'w') as f:
                f.write(spreadsheet_id)
    except FileNotFoundError:
        print("  No existing sheet. Creating new...")
        spreadsheet_id, sheet_gid = create_sheet(sheets_service)
        setup_sheet_headers_and_formatting(sheets_service, spreadsheet_id, sheet_gid)
        with open(SHEET_ID_PATH, 'w') as f:
            f.write(spreadsheet_id)
    except Exception as e:
        print(f"  Error checking existing sheet ({e}). Creating new...")
        spreadsheet_id, sheet_gid = create_sheet(sheets_service)
        setup_sheet_headers_and_formatting(sheets_service, spreadsheet_id, sheet_gid)
        with open(SHEET_ID_PATH, 'w') as f:
            f.write(spreadsheet_id)

    print(f"  Using Sheet ID: {spreadsheet_id}")
    print(f"  URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")

    # ── STEP 2: Gmail ──
    gmail_apps = scan_gmail(gmail_svc)

    # ── STEP 3: MSN ──
    msn_apps = scan_msn(msn_token)

    # ── Combine ──
    all_apps = gmail_apps + msn_apps
    print(f"\n  Combined: {len(all_apps)} applications (Gmail: {len(gmail_apps)}, MSN: {len(msn_apps)})")

    # ── STEP 6: Deduplicate ──
    applications, status_counts = deduplicate(all_apps)

    # ── Print Summary ──
    print(f"\n{'='*70}")
    print(f"FINAL: {len(applications)} unique job applications")
    print(f"{'='*70}")
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"  {status:<25} {count}")
    print(f"\nTop applications (newest first):")
    for app in applications[:30]:
        print(f"  [{app['date_applied']}] {app['company']:<22} | {app['position'][:35]:<35} | {app['status']:<22} | {app['platform']}")

    # ── STEP 7: Write to sheet ──
    write_to_sheet(sheets_service, spreadsheet_id, applications)

    # ── STEP 8: Save state ──
    save_state(spreadsheet_id, applications, status_counts)

    print(f"\n{'='*70}")
    print("DONE!")
    print(f"  Sheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
    print(f"  Total: {len(applications)} applications")
    print(f"  State: {APPS_JSON_PATH}")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
