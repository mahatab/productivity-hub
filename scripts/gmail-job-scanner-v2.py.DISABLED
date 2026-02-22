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
    return text[:10000]

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
    internal = msg.get('internalDate', '0')
    ts = int(internal) / 1000
    return datetime.fromtimestamp(ts).date()

PLATFORM_MAP = {
    'linkedin.com': 'LinkedIn',
    'greenhouse.io': 'Greenhouse',
    'lever.co': 'Lever',
    'workday.com': 'Workday',
    'myworkdayjobs.com': 'Workday',
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
    'glassdoor.com': 'Glassdoor',
    'wellfound.com': 'Wellfound',
    'angel.co': 'AngelList',
    'dice.com': 'Dice',
    'monster.com': 'Monster',
    'careerbuilder.com': 'CareerBuilder',
    'workable.com': 'Workable',
    'jazz.co': 'JazzHR',
    'pinpointhq.com': 'Pinpoint',
    'applytojob.com': 'ApplyToJob',
    'hirehive.io': 'HireHive',
    'personio.de': 'Personio',
    'recruitcrm.io': 'RecruitCRM',
    'rippling.com': 'Rippling',
    'gusto.com': 'Gusto',
    'eightfold.ai': 'Eightfold',
    'paradox.ai': 'Paradox/Olivia',
    'greenhouse-mail.io': 'Greenhouse',
    'myworkday.com': 'Workday',
}

# Domains/keywords that clearly indicate NON-job emails
NON_JOB_KEYWORDS = [
    'loan', 'emi', 'credit card', 'debit card', 'bank account', 'banking',
    'order number', 'order confirmed', 'order placed', 'shipment', 'delivery',
    'invoice', 'payment', 'transaction', 'otp', 'verification code',
    'password reset', 'account verification', 'email verification',
    'subscription', 'renewal', 'upgrade your plan',
    'sale', 'discount', 'offer expires', 'promo code',
    'newsletter', 'unsubscribe',
    'car dealer', 'salesztrac', 'vehicle',
    'mutual fund', 'insurance premium', 'policy',
]

def is_job_application_email(subject, text, sender):
    """Filter out obvious non-job emails."""
    combined_lower = (subject + ' ' + text[:1000]).lower()

    # Must contain job-related keywords
    job_keywords = [
        'apply', 'applied', 'application', 'position', 'role', 'job',
        'career', 'hiring', 'recruit', 'candidate', 'resume', 'cv',
        'opening', 'opportunity', 'interview', 'screening', 'offer',
        'hiring team', 'talent', 'onboard'
    ]

    # Check for non-job signals
    non_job_count = sum(1 for kw in NON_JOB_KEYWORDS if kw in combined_lower)
    if non_job_count >= 2:
        return False

    # Must have at least one job keyword
    job_count = sum(1 for kw in job_keywords if kw in combined_lower)
    if job_count == 0:
        return False

    # Sender domain checks
    sender_lower = sender.lower()
    non_job_domains = [
        'hdbfs', 'hdfc', 'sbi', 'icici', 'axis', 'kotak',
        'jio.com', 'amazon.in', 'flipkart', 'myntra',
        'marutidealers', 'maruti', 'hyundai.in',
        'irctc', 'bookmyshow',
    ]
    for d in non_job_domains:
        if d in sender_lower:
            return False

    return True

def detect_platform(sender, text):
    sender_lower = sender.lower()
    text_lower = text[:3000].lower()
    for domain, platform in PLATFORM_MAP.items():
        if domain in sender_lower:
            return platform
    for domain, platform in PLATFORM_MAP.items():
        if domain in text_lower:
            return platform
    return 'Direct/Other'

def extract_company(sender, subject, text):
    # Try from sender display name first
    name_match = re.match(r'^"?([^"<@\n]{2,50}?)"?\s*<', sender)
    if name_match:
        display = name_match.group(1).strip()
        # Skip generic names
        if not any(skip in display.lower() for skip in ['noreply', 'no-reply', 'notification', 'team', 'recruiting', 'careers', 'info', 'jobs', 'talent', 'hr']):
            if not re.match(r'^[\w\.\-]+@', display):  # Not an email address
                return display.title()

    # Try from sender domain
    sender_match = re.search(r'@([^>@\s]+)', sender)
    if sender_match:
        domain = sender_match.group(1).lower()
        is_platform = any(p in domain for p in list(PLATFORM_MAP.keys()) + ['gmail', 'yahoo', 'outlook', 'hotmail'])
        if not is_platform:
            parts = domain.split('.')
            if len(parts) >= 2:
                company = parts[-2]
                company = re.sub(r'[-_]', ' ', company).title()
                skip_words = ['mail', 'email', 'noreply', 'no', 'info', 'jobs', 'careers', 'recruiting', 'talent', 'hr', 'notifications', 'notification', 'donotreply', 'apply']
                if company.lower() not in skip_words and len(company) > 2:
                    return company

    # From body text patterns
    body_patterns = [
        r'(?:Thank you for applying to|applied to|application to|position at|role at|joining)\s+([A-Z][A-Za-z0-9\s&\-\.]{2,40}?)(?:\s*[,\.\n!]|\s+team|\s+for|\s+is)',
        r'(?:from|at|with)\s+([A-Z][A-Za-z0-9\s&\-\.]{2,40}?)\s+(?:Recruiting|Talent|HR|Careers)',
    ]
    for pat in body_patterns:
        m = re.search(pat, text[:4000])
        if m:
            company = m.group(1).strip().rstrip(' ,-.')
            if len(company) > 2 and company.lower() not in ['the', 'we', 'our', 'you', 'your', 'this']:
                return company

    # From subject
    sub_patterns = [
        r'(?:application|applying|applied)(?:\s+to|\s+at|\s+for|\s+with)?\s+([A-Z][A-Za-z0-9\s&\-]{2,40}?)(?:\s*[-–@\(]|\s+is|\s+has|$)',
    ]
    for pat in sub_patterns:
        m = re.search(pat, subject, re.IGNORECASE)
        if m:
            company = m.group(1).strip()
            if len(company) > 2:
                return company

    return 'Unknown'

def extract_position(subject, text):
    # Position from subject
    patterns = [
        r'(?:applied for|application for|applying for|your application[:\s]+for)[:\s]+(?:the\s+)?(?:role of\s+|position of\s+|position:\s+)?(?:a\s+|an\s+)?([A-Za-z][A-Za-z0-9\s\-,/&\(\)]{5,80}?)(?:\s+(?:at|with|position|role)|[-–@\(]|[,\.]|$)',
        r'(?:role|position|job|opening|opportunity)[:\s]+([A-Za-z][A-Za-z0-9\s\-,/&\(\)]{5,60}?)(?:\s+at|\s+\(|[,\.\n]|$)',
    ]
    for pat in patterns:
        m = re.search(pat, subject, re.IGNORECASE)
        if m:
            pos = m.group(1).strip().rstrip(' -–,.')
            if len(pos) > 3 and pos.lower() not in ['the', 'a', 'an', 'your', 'our', 'this']:
                return pos[:100]

    # From body
    body_patterns = [
        r'(?:applied for|application for|applying for)[:\s]+(?:the\s+)?([A-Za-z][A-Za-z0-9\s\-,/&]{5,80}?)(?:\s+(?:position|role|job)|[,\.\n]|$)',
        r'(?:Position|Role|Job Title|Job)[:\s]+([A-Za-z][A-Za-z0-9\s\-,/&\(\)]{5,60}?)(?:[,\.\n]|$)',
        r'(?:You applied for|application for)\s+([A-Za-z][A-Za-z0-9\s\-,/&]{5,60}?)(?:\s+(?:at|with)|[,\.\n]|$)',
    ]
    for pat in body_patterns:
        m = re.search(pat, text[:5000], re.IGNORECASE)
        if m:
            pos = m.group(1).strip().rstrip(' -–,.')
            if len(pos) > 3:
                return pos[:100]

    # Fallback: clean up subject
    subject_clean = re.sub(r'^(?:re:|fw:|fwd:)\s*', '', subject, flags=re.IGNORECASE).strip()
    subject_clean = re.sub(r'(?:application|confirmation|received|submitted|thank you|applying|applied)[^-–]*$', '', subject_clean, flags=re.IGNORECASE).strip()
    subject_clean = subject_clean.rstrip(' -–@|').strip()
    if subject_clean and len(subject_clean) > 5:
        return subject_clean[:100]

    return 'Unknown Position'

def extract_job_id(text):
    param_patterns = [
        r'(?:jobId|job_id|job-id|gh_jid|jid|req_id|reqId|req-id|requisition[_-]?id|jobReqId|jobcode|jobCode|jobref|jobRef)=([A-Za-z0-9_\-]+)',
        r'/jobs?/([A-Za-z0-9_\-]{5,30})(?:[/?#]|$)',
        r'/positions?/([A-Za-z0-9_\-]{4,30})(?:[/?#]|$)',
        r'(?:Job\s*(?:ID|#|Number|Req)[:\s#]+)([A-Za-z0-9_\-]{4,30})',
        r'(?:Req(?:uisition)?\s*(?:ID|#|Number)[:\s#]+)([A-Za-z0-9_\-]{4,30})',
        r'(?:Posting\s*(?:ID|#)[:\s#]+)([A-Za-z0-9_\-]{4,30})',
    ]
    for pat in param_patterns:
        m = re.search(pat, text[:10000], re.IGNORECASE)
        if m:
            jid = m.group(1)
            if len(jid) >= 4 and jid.lower() not in ['apply', 'jobs', 'careers', 'view', 'edit', 'new', 'create', 'open', 'list']:
                return jid
    return 'N/A'

def determine_status(all_msgs):
    """Determine status from all messages in thread (last message wins for escalated states)."""
    combined_all = ''
    for msg in all_msgs:
        subject = get_header(msg, 'Subject')
        text = get_email_text(msg)
        combined_all = subject + ' ' + text + '\n' + combined_all

    combined = combined_all.lower()

    # Interview signals
    interview_patterns = [
        'phone interview', 'video interview', 'virtual interview',
        'interview scheduled', 'interview invitation', 'interview request',
        'phone screen', 'technical screen', 'technical interview',
        'hiring manager', 'schedule a call with', 'schedule time',
        'we would like to invite you', 'we\'d like to invite you',
        'next round', 'move you forward', 'move you to the next',
        'assessment link', 'coding challenge', 'take-home assignment',
        'hackerrank', 'codility', 'pymetrics', 'predictive index',
    ]
    for p in interview_patterns:
        if p in combined:
            return 'Interview Scheduled'

    # Rejection signals
    rejection_patterns = [
        'not moving forward', 'not selected', 'decided to move forward with other',
        'decided to pursue other candidates', 'will not be moving',
        'regret to inform', 'unfortunately', 'not a fit', 'not the right fit',
        'position has been filled', 'will not be proceeding',
        'decided to go with', 'decided not to move',
        'after careful consideration, we have decided',
        'we have decided to move forward with another',
        'we won\'t be moving', 'cannot move forward',
        'not be moving forward', 'we are not able to',
        'we\'ve decided to', 'thank you for your time.*unfortunately',
    ]
    for p in rejection_patterns:
        if re.search(p, combined):
            return 'Rejected'

    # Under review signals
    review_patterns = [
        'under review', 'reviewing your application', 'being reviewed',
        'in review', 'actively screening', 'shortlisting', 'next steps',
        'will be in touch', 'keep you updated',
    ]
    for p in review_patterns:
        if p in combined:
            return 'Under Review'

    return 'Applied'

def extract_notes(text, sender):
    notes_parts = []

    # Job URL
    url_match = re.search(r'https?://[^\s<>"]{10,200}(?:job|career|position|apply|req|opening)[^\s<>"]{0,150}', text, re.IGNORECASE)
    if url_match:
        url = url_match.group(0).rstrip('.,)')
        notes_parts.append(f'URL: {url[:200]}')

    # Location
    loc_patterns = [
        r'(?:Location|Office|City|Based in)[:\s]+([A-Za-z\s,]{5,50}?)(?:\n|\.|$)',
        r'\b(Remote|Hybrid|On-site|Onsite|In-office)\b',
    ]
    for pat in loc_patterns:
        m = re.search(pat, text[:4000], re.IGNORECASE)
        if m:
            loc = m.group(1).strip() if m.lastindex else m.group(0)
            notes_parts.append(f'Location: {loc[:60]}')
            break

    # Salary
    salary_match = re.search(r'\$[\d,]+(?:\s*[-–to]+\s*\$[\d,]+)?(?:\s*(?:k|K|per year|\/yr|annually))?', text)
    if salary_match:
        notes_parts.append(f'Salary: {salary_match.group(0)}')

    return ' | '.join(notes_parts)[:500]

def search_gmail_messages(gmail_service, query):
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
    return gmail_service.users().messages().get(userId='me', id=msg_id, format='full').execute()

def main():
    creds = get_creds()
    gmail_service = build('gmail', 'v1', credentials=creds)

    # Original queries + additional targeted ones
    queries = [
        '"you applied for" after:2025/11/01 before:2026/02/18',
        '"your application was sent" after:2025/11/01 before:2026/02/18',
        '"we received your application" after:2025/11/01 before:2026/02/18',
        '"thank you for applying" after:2025/11/01 before:2026/02/18',
        '"application confirmation" after:2025/11/01 before:2026/02/18',
        '"application submitted" after:2025/11/01 before:2026/02/18',
        '"we have received your application" after:2025/11/01 before:2026/02/18',
        'subject:("application received") after:2025/11/01 before:2026/02/18',
        # Additional targeted queries
        '"your application has been" after:2025/11/01 before:2026/02/18',
        '"applied to" (job OR position OR role) after:2025/11/01 before:2026/02/18',
        'from:greenhouse.io after:2025/11/01 before:2026/02/18',
        'from:lever.co after:2025/11/01 before:2026/02/18',
        'from:linkedin.com (applied OR application) after:2025/11/01 before:2026/02/18',
        'from:workday.com after:2025/11/01 before:2026/02/18',
        'from:myworkdayjobs.com after:2025/11/01 before:2026/02/18',
        'from:icims.com after:2025/11/01 before:2026/02/18',
        'from:smartrecruiters.com after:2025/11/01 before:2026/02/18',
        'from:jobvite.com after:2025/11/01 before:2026/02/18',
        'from:ashbyhq.com after:2025/11/01 before:2026/02/18',
        '"we are reviewing" (application OR resume OR cv) after:2025/11/01 before:2026/02/18',
        '"your resume" (received OR reviewing OR considered) after:2025/11/01 before:2026/02/18',
        '"not moving forward" after:2025/11/01 before:2026/02/18',
        '"not selected" (application OR position OR role) after:2025/11/01 before:2026/02/18',
        '"interview" (scheduled OR invitation) (position OR role OR application) after:2025/11/01 before:2026/02/18',
        'subject:(application) (position OR role OR job) after:2025/11/01 before:2026/02/18',
        '"thank you for your application" after:2025/11/01 before:2026/02/18',
        '"we appreciate your interest" (position OR role OR job) after:2025/11/01 before:2026/02/18',
    ]

    all_msg_ids = set()
    print("Searching Gmail for job application emails...")
    for q in queries:
        msgs = search_gmail_messages(gmail_service, q)
        ids = {m['id'] for m in msgs}
        if ids:
            print(f"  [{len(ids):3d}] {q[:80]}")
        all_msg_ids.update(ids)

    print(f"\nTotal unique messages found: {len(all_msg_ids)}")

    # Fetch and group by thread
    thread_msgs = {}
    msg_list = list(all_msg_ids)
    print(f"Fetching {len(msg_list)} messages...")

    for i, msg_id in enumerate(msg_list):
        if i % 10 == 0 and i > 0:
            print(f"  {i}/{len(msg_list)} processed...")
        try:
            msg = fetch_message(gmail_service, msg_id)
            thread_id = msg.get('threadId', msg_id)
            if thread_id not in thread_msgs:
                thread_msgs[thread_id] = []
            thread_msgs[thread_id].append(msg)
        except Exception as e:
            print(f"  Warning: Failed to fetch {msg_id}: {e}")

    print(f"Processing {len(thread_msgs)} threads...")

    applications = []
    filtered_out = []

    for thread_id, msgs in thread_msgs.items():
        msgs.sort(key=lambda m: parse_email_date(m))
        first_msg = msgs[0]
        last_msg = msgs[-1]

        subject = get_header(first_msg, 'Subject')
        sender = get_header(first_msg, 'From')
        date_applied = parse_email_date(first_msg)
        last_update_date = parse_email_date(last_msg)

        all_text = ''
        for m in msgs:
            all_text += get_email_text(m) + '\n'

        # Filter non-job emails
        if not is_job_application_email(subject, all_text, sender):
            filtered_out.append(f"  FILTERED: {subject[:60]} (from: {sender[:40]})")
            continue

        platform = detect_platform(sender, all_text)
        company = extract_company(sender, subject, all_text)
        position = extract_position(subject, all_text)
        job_id = extract_job_id(all_text)
        status = determine_status(msgs)

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

    print(f"\nFiltered out {len(filtered_out)} non-job emails:")
    for f in filtered_out:
        print(f)

    # Deduplication
    deduped = {}
    for app in applications:
        if app['job_id'] != 'N/A':
            key = f"{app['job_id']}|{app['company'].lower()}"
        else:
            key = f"{app['company'].lower()}|{app['position'].lower()[:30]}|{app['date_applied']}"

        if key in deduped:
            existing = deduped[key]
            status_priority = {'Interview Scheduled': 4, 'Under Review': 3, 'Rejected': 2, 'Applied': 1}
            if status_priority.get(app['status'], 0) > status_priority.get(existing['status'], 0):
                existing['status'] = app['status']
            if app['last_update'] > existing['last_update']:
                existing['last_update'] = app['last_update']
            # Merge notes
            if app['notes'] and app['notes'] not in existing['notes']:
                existing['notes'] = (existing['notes'] + ' | ' + app['notes'])[:500]
        else:
            deduped[key] = app

    applications = list(deduped.values())
    applications.sort(key=lambda x: x['date_applied_raw'], reverse=True)

    # Clean up non-serializable fields
    for app in applications:
        app.pop('date_applied_raw', None)

    print(f"\n{'='*60}")
    print(f"FINAL: {len(applications)} unique job applications")
    print(f"{'='*60}")

    status_counts = {}
    for app in applications:
        status_counts[app['status']] = status_counts.get(app['status'], 0) + 1

    print("Status breakdown:")
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"  {status}: {count}")

    print("\nAll applications:")
    for app in applications:
        print(f"  [{app['date_applied']}] {app['company']:<25} | {app['position'][:40]:<40} | {app['status']:<20} | {app['platform']}")

    with open('/tmp/job-applications-data.json', 'w') as f:
        json.dump({'applications': applications, 'status_counts': status_counts, 'total': len(applications)}, f, indent=2)

    print(f"\nData saved to /tmp/job-applications-data.json")
    return applications, status_counts

if __name__ == '__main__':
    main()
