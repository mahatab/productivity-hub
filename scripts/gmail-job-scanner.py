import sys, json, warnings, os, re, base64
from datetime import datetime, date
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser

warnings.filterwarnings('ignore')
sys.path.insert(0, '/Users/mahatabrashid/Library/Python/3.9/lib/python/site-packages')

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PATH = os.path.expanduser('~/.clawdbot/gmail/token.json')
TODAY = date(2026, 2, 17)

def get_creds():
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
        data['token'] = creds.token
        with open(TOKEN_PATH, 'w') as f:
            json.dump(data, f, indent=2)
    return creds

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

def decode_body(part):
    """Decode a base64url encoded email part."""
    data = part.get('body', {}).get('data', '')
    if data:
        return base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace')
    return ''

def extract_text_from_parts(parts):
    plain = ''
    html = ''
    for part in parts:
        mime = part.get('mimeType', '')
        if mime == 'text/plain':
            plain += decode_body(part)
        elif mime == 'text/html':
            html += decode_body(part)
        elif mime.startswith('multipart/'):
            sub_parts = part.get('parts', [])
            p, h = extract_text_from_parts(sub_parts)
            plain += p
            html += h
    return plain, html

def get_email_text(msg):
    payload = msg.get('payload', {})
    mime = payload.get('mimeType', '')
    plain = ''
    html = ''
    if mime == 'text/plain':
        plain = decode_body(payload)
    elif mime == 'text/html':
        html = decode_body(payload)
    elif mime.startswith('multipart/'):
        parts = payload.get('parts', [])
        plain, html = extract_text_from_parts(parts)
    text = plain if plain else html_to_text(html) if html else ''
    return text[:8000]  # limit to 8K chars

def get_header(msg, name):
    headers = msg.get('payload', {}).get('headers', [])
    for h in headers:
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
    # fallback to internalDate
    internal = msg.get('internalDate', '0')
    ts = int(internal) / 1000
    return datetime.fromtimestamp(ts).date()

PLATFORM_MAP = {
    'linkedin.com': 'LinkedIn',
    'greenhouse.io': 'Greenhouse',
    'lever.co': 'Lever',
    'workday.com': 'Workday',
    'icims.com': 'iCIMS',
    'smartrecruiters.com': 'SmartRecruiters',
    'taleo.net': 'Taleo',
    'jobvite.com': 'Jobvite',
    'ashbyhq.com': 'Ashby',
    'myworkdayjobs.com': 'Workday',
    'successfactors.com': 'SAP SuccessFactors',
    'breezy.hr': 'Breezy',
    'bamboohr.com': 'BambooHR',
    'recruitee.com': 'Recruitee',
    'indeed.com': 'Indeed',
    'ziprecruiter.com': 'ZipRecruiter',
    'glassdoor.com': 'Glassdoor',
    'wellfound.com': 'Wellfound',
    'angel.co': 'AngelList',
    'dice.com': 'Dice',
    'monster.com': 'Monster',
    'careerbuilder.com': 'CareerBuilder',
}

def detect_platform(sender, text):
    sender_lower = sender.lower()
    text_lower = text.lower()
    for domain, platform in PLATFORM_MAP.items():
        if domain in sender_lower:
            return platform
    for domain, platform in PLATFORM_MAP.items():
        if domain in text_lower:
            return platform
    return 'Direct/Other'

def extract_company(sender, subject, text):
    """Extract company name from sender domain or email body."""
    # Try from sender
    sender_match = re.search(r'@([^>@\s]+)', sender)
    if sender_match:
        domain = sender_match.group(1).lower()
        # Remove known platform domains
        is_platform = any(p in domain for p in PLATFORM_MAP.keys())
        if not is_platform:
            # Extract company from domain
            parts = domain.split('.')
            if len(parts) >= 2:
                company = parts[-2]
                # Clean up
                company = company.replace('-', ' ').replace('_', ' ').title()
                if company.lower() not in ['mail', 'email', 'noreply', 'no', 'info', 'jobs', 'careers', 'recruiting', 'talent', 'hr', 'notifications', 'notification']:
                    return company

    # Try "from XYZ team" / "XYZ recruiting" patterns in subject
    patterns = [
        r'(?:from|at|@)\s+([A-Z][A-Za-z0-9&\-\s]{2,30}?)(?:\s+team|\s+Recruiting|\s+HR|\s+Careers|[,\.]|$)',
        r'^([A-Z][A-Za-z0-9&\-\s]{2,30}?)(?:\s+is|\s+has|\s+would|\s+wants)',
    ]
    for pat in patterns:
        m = re.search(pat, subject)
        if m:
            company = m.group(1).strip()
            if len(company) > 2:
                return company

    # Try "at [Company]" or "with [Company]" in text
    body_patterns = [
        r'(?:at|with|from|join)\s+([A-Z][A-Za-z0-9&\-\s]{2,30}?)(?:\s+is|\s+has|\s+team|\s+careers|[,\.\n])',
        r'([A-Z][A-Za-z0-9&\-\s]{2,30}?)\s+(?:is excited|would like|thanks you|received your)',
    ]
    for pat in body_patterns:
        m = re.search(pat, text[:2000])
        if m:
            company = m.group(1).strip()
            if len(company) > 2 and company.lower() not in ['the', 'we', 'our', 'you', 'your']:
                return company

    # Last resort: use sender name
    name_match = re.match(r'^([^<]+)<', sender)
    if name_match:
        name = name_match.group(1).strip().strip('"').strip("'")
        if name and len(name) > 2:
            return name

    return 'Unknown'

def extract_position(subject, text):
    """Extract job position from subject or body."""
    # Common subject patterns
    patterns = [
        r'(?:applied for|application for|applying for|your application[:\s]+)(?:the\s+)?(?:role of\s+|position of\s+|position:\s+)?([A-Za-z][A-Za-z0-9\s\-,/&]+?)(?:\s+at|\s+with|\s+position|\s*[-–]|\s*\(|$)',
        r'(?:role|position|job|opening)[:\s]+([A-Za-z][A-Za-z0-9\s\-,/&]{5,60}?)(?:\s+at|\s+\(|[,\.\n]|$)',
        r'^(?:re:|fw:|fwd:)?\s*(?:application[:\s]+)?([A-Za-z][A-Za-z0-9\s\-,/&]{5,60}?)(?:\s+[-–@]|\s+at\s|\s+application|\s*\(|$)',
    ]
    for pat in patterns:
        m = re.search(pat, subject, re.IGNORECASE)
        if m:
            pos = m.group(1).strip().rstrip(' -–')
            if len(pos) > 3 and pos.lower() not in ['the', 'a', 'an', 'your', 'our']:
                return pos[:100]

    # Try from body
    body_patterns = [
        r'(?:applied for|application for|applying for)[:\s]+(?:the\s+)?([A-Za-z][A-Za-z0-9\s\-,/&]{5,60}?)(?:\s+(?:position|role|job)|[,\.\n]|$)',
        r'(?:position|role|job title)[:\s]+([A-Za-z][A-Za-z0-9\s\-,/&]{5,60}?)(?:[,\.\n]|$)',
    ]
    for pat in body_patterns:
        m = re.search(pat, text[:3000], re.IGNORECASE)
        if m:
            pos = m.group(1).strip().rstrip(' -–')
            if len(pos) > 3:
                return pos[:100]

    # If subject looks like a position title itself
    subject_clean = re.sub(r'^(?:re:|fw:|fwd:)\s*', '', subject, flags=re.IGNORECASE).strip()
    subject_clean = re.sub(r'(?:application|confirmation|received|submitted|thank you)[^\-]*$', '', subject_clean, flags=re.IGNORECASE).strip().rstrip(' -–@')
    if subject_clean and len(subject_clean) > 5:
        return subject_clean[:100]

    return 'Unknown Position'

def extract_job_id(text, url_text=''):
    """Extract job ID from URL params or body text."""
    # URL param patterns
    param_patterns = [
        r'(?:jobId|job_id|job-id|gh_jid|jid|req_id|reqId|req-id|requisition[_-]?id|jobReqId|jobcode|jobCode|jobref|jobRef|id)=([A-Za-z0-9_\-]+)',
        r'/jobs?/([A-Za-z0-9_\-]{6,30})(?:[/?#]|$)',
        r'/positions?/([A-Za-z0-9_\-]{4,30})(?:[/?#]|$)',
        r'(?:Job\s*(?:ID|#|Number|Req)[:\s#]+)([A-Za-z0-9_\-]{4,30})',
        r'(?:Req(?:uisition)?\s*(?:ID|#|Number)[:\s#]+)([A-Za-z0-9_\-]{4,30})',
    ]
    combined_text = (text + ' ' + url_text)[:10000]
    for pat in param_patterns:
        m = re.search(pat, combined_text, re.IGNORECASE)
        if m:
            jid = m.group(1)
            if len(jid) >= 4 and jid.lower() not in ['apply', 'jobs', 'careers', 'view', 'edit', 'new', 'create']:
                return jid
    return 'N/A'

def determine_status(subject, text):
    """Determine application status from email content."""
    combined = (subject + ' ' + text).lower()

    # Interview signals
    interview_patterns = [
        'interview', 'phone screen', 'technical screen', 'hiring manager',
        'schedule a call', 'schedule time', 'next steps', 'meet with',
        'video call', 'zoom', 'teams meeting', 'assessment', 'coding challenge',
        'take-home', 'technical assessment'
    ]
    for p in interview_patterns:
        if p in combined:
            return 'Interview Scheduled'

    # Rejection signals
    rejection_patterns = [
        'not moving forward', 'not selected', 'decided to move forward with other',
        'decided to pursue other', 'will not be moving', 'unfortunately',
        'regret to inform', 'not a fit', 'not the right fit', 'position has been filled',
        'filled the position', 'decline', 'rejected', 'not successful',
        'we have decided not', 'we will not', 'other candidates', 'other applicants',
        'not an opportunity', 'no longer accepting', 'position is no longer',
        'we won\'t be', 'after careful consideration', 'decided to go with',
        'not be moving forward', 'cannot move forward', 'not be proceeding'
    ]
    for p in rejection_patterns:
        if p in combined:
            return 'Rejected'

    # Under review signals
    review_patterns = [
        'under review', 'reviewing your application', 'being reviewed',
        'in review', 'screening', 'shortlisting', 'pipeline'
    ]
    for p in review_patterns:
        if p in combined:
            return 'Under Review'

    return 'Applied'

def extract_notes(text, sender):
    """Extract useful notes: recruiter, location, salary, URL."""
    notes_parts = []

    # Job URL
    url_match = re.search(r'(?:https?://[^\s<>"]{20,200}(?:job|career|position|apply|req)[^\s<>"]{0,100})', text, re.IGNORECASE)
    if url_match:
        url = url_match.group(0).rstrip('.,)')
        notes_parts.append(f'URL: {url[:150]}')

    # Recruiter name
    recruiter_patterns = [
        r'(?:regards|sincerely|best|thanks)[,\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*\n',
        r'(?:recruiter|talent|hiring)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*\|\s*(?:recruiter|talent|sourcer)',
    ]
    for pat in recruiter_patterns:
        m = re.search(pat, text[:3000], re.IGNORECASE | re.MULTILINE)
        if m:
            recruiter = m.group(1).strip()
            if len(recruiter) > 2:
                notes_parts.append(f'Recruiter: {recruiter}')
            break

    # Location
    loc_patterns = [
        r'(?:location|office|based in|position is in)[:\s]+([A-Za-z\s,]{5,50}?)(?:\n|\.|\||$)',
        r'(?:Remote|Hybrid|On-?site)',
    ]
    for pat in loc_patterns:
        m = re.search(pat, text[:3000], re.IGNORECASE)
        if m:
            loc = m.group(0).strip()[:50]
            notes_parts.append(f'Location: {loc}')
            break

    # Salary
    salary_match = re.search(r'\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?(?:\s*(?:k|K|per year|\/yr|annually))?', text)
    if salary_match:
        notes_parts.append(f'Salary: {salary_match.group(0)}')

    return ' | '.join(notes_parts)[:500]

def search_gmail_messages(gmail_service, query):
    """Search Gmail and return all message IDs matching query."""
    messages = []
    page_token = None
    while True:
        kwargs = {'userId': 'me', 'q': query, 'maxResults': 100}
        if page_token:
            kwargs['pageToken'] = page_token
        result = gmail_service.users().messages().list(**kwargs).execute()
        batch = result.get('messages', [])
        messages.extend(batch)
        page_token = result.get('nextPageToken')
        if not page_token:
            break
    return messages

def fetch_message(gmail_service, msg_id):
    return gmail_service.users().messages().get(
        userId='me', id=msg_id, format='full'
    ).execute()

def main():
    creds = get_creds()
    gmail_service = build('gmail', 'v1', credentials=creds)

    queries = [
        '"you applied for" after:2025/11/01 before:2026/02/18',
        '"your application was sent" after:2025/11/01 before:2026/02/18',
        '"we received your application" after:2025/11/01 before:2026/02/18',
        '"thank you for applying" after:2025/11/01 before:2026/02/18',
        '"application confirmation" after:2025/11/01 before:2026/02/18',
        '"application submitted" after:2025/11/01 before:2026/02/18',
        '"we have received your application" after:2025/11/01 before:2026/02/18',
        'subject:("application received") after:2025/11/01 before:2026/02/18',
    ]

    # Collect all unique message IDs
    all_msg_ids = set()
    print("Searching Gmail for job application emails...")
    for q in queries:
        msgs = search_gmail_messages(gmail_service, q)
        ids = {m['id'] for m in msgs}
        print(f"  Query: {q[:60]}... → {len(ids)} messages")
        all_msg_ids.update(ids)

    print(f"\nTotal unique messages to process: {len(all_msg_ids)}")

    # Group by thread
    thread_map = {}  # thread_id → list of msg_ids
    thread_data = {}  # thread_id → processed info

    msg_list = list(all_msg_ids)
    print(f"Fetching {len(msg_list)} messages...")

    for i, msg_id in enumerate(msg_list):
        if i % 10 == 0:
            print(f"  Processing message {i+1}/{len(msg_list)}...")
        try:
            msg = fetch_message(gmail_service, msg_id)
            thread_id = msg.get('threadId', msg_id)
            if thread_id not in thread_map:
                thread_map[thread_id] = []
            thread_map[thread_id].append(msg)
        except Exception as e:
            print(f"  Warning: Failed to fetch message {msg_id}: {e}")

    print(f"\nProcessing {len(thread_map)} unique threads...")

    applications = []  # list of dicts

    for thread_id, msgs in thread_map.items():
        # Sort by date
        msgs.sort(key=lambda m: parse_email_date(m))
        first_msg = msgs[0]
        last_msg = msgs[-1]

        subject = get_header(first_msg, 'Subject')
        sender = get_header(first_msg, 'From')
        date_applied = parse_email_date(first_msg)
        last_update_date = parse_email_date(last_msg)

        # Get text from all messages in thread
        all_text = ''
        for m in msgs:
            all_text += get_email_text(m) + '\n'

        platform = detect_platform(sender, all_text)
        company = extract_company(sender, subject, all_text)
        position = extract_position(subject, all_text)
        job_id = extract_job_id(all_text)

        # Determine status from ALL emails in thread (especially last one)
        last_text = get_email_text(last_msg)
        last_subject = get_header(last_msg, 'Subject')
        status = determine_status(last_subject, last_text)

        days_since = (TODAY - date_applied).days
        follow_up = 'YES' if status in ('Applied', 'No Response') and days_since > 14 else 'NO'

        notes = extract_notes(all_text, sender)

        app = {
            'job_id': job_id,
            'company': company,
            'position': position,
            'date_applied': date_applied.strftime('%m/%d/%Y'),
            'date_applied_raw': date_applied,
            'platform': platform,
            'status': status,
            'last_update': last_update_date.strftime('%m/%d/%Y'),
            'follow_up': follow_up,
            'days_since': days_since,
            'notes': notes,
            'thread_id': thread_id,
        }
        applications.append(app)

    # Deduplication: use job_id+company or company+position+date
    deduped = {}
    for app in applications:
        if app['job_id'] != 'N/A':
            key = f"{app['job_id']}|{app['company'].lower()}"
        else:
            key = f"{app['company'].lower()}|{app['position'].lower()[:30]}|{app['date_applied']}"

        if key in deduped:
            existing = deduped[key]
            # Keep most recent update, worst case status escalation
            status_priority = {'Interview Scheduled': 4, 'Under Review': 3, 'Rejected': 2, 'Applied': 1}
            if status_priority.get(app['status'], 0) > status_priority.get(existing['status'], 0):
                existing['status'] = app['status']
            if app['last_update'] > existing['last_update']:
                existing['last_update'] = app['last_update']
        else:
            deduped[key] = app

    applications = list(deduped.values())

    # Sort by date applied descending (newest first)
    applications.sort(key=lambda x: x['date_applied_raw'], reverse=True)

    print(f"\nFound {len(applications)} unique job applications after deduplication.")

    # Status breakdown
    status_counts = {}
    for app in applications:
        status_counts[app['status']] = status_counts.get(app['status'], 0) + 1

    print("\nStatus breakdown:")
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"  {status}: {count}")

    # Save to file for the sheet writer
    output_path = '/tmp/job-applications-data.json'
    # Convert dates to strings for JSON
    for app in applications:
        app.pop('date_applied_raw', None)

    with open(output_path, 'w') as f:
        json.dump({
            'applications': applications,
            'status_counts': status_counts,
            'total': len(applications)
        }, f, indent=2)

    print(f"\nData saved to {output_path}")
    return applications, status_counts

if __name__ == '__main__':
    apps, counts = main()
    print("\nSample applications (first 5):")
    for app in apps[:5]:
        print(f"  {app['company']} | {app['position'][:40]} | {app['date_applied']} | {app['status']}")
