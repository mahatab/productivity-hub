#!/usr/bin/env python3
"""
Job Application Tracker - Smart v2
Uses thread-level search to avoid fetching 500+ individual messages.
"""

import sys, os, json, re, base64, datetime, time, urllib.request, urllib.parse, traceback

# ── paths ──────────────────────────────────────────────────────────────────────
SHEET_ID   = "1d9OS6SEJWgJkDyYbTYiGB-4Jj3RsXz7CFNnwz-6E5X8"
GMAIL_TOKEN = os.path.expanduser("~/.clawdbot/gmail/token.json")
MSN_TOKEN   = os.path.expanduser("~/.clawdbot/msn/token.json")
MSN_CLIENT_ID = "7ed8b008-8f80-4c57-a7be-773210b67021"
STATE_FILE  = "/Users/mahatabrashid/clawd/memory/job-applications.json"
LOG_FILE    = "/tmp/job-tracker-run2.log"
TODAY       = datetime.date(2026, 2, 17)

sys.path.insert(0, "/Users/mahatabrashid/Library/Python/3.9/lib/python/site-packages")

# ── logging ────────────────────────────────────────────────────────────────────
import atexit
_log_fh = open(LOG_FILE, "w", buffering=1)
def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    _log_fh.write(line + "\n")
    _log_fh.flush()
atexit.register(_log_fh.close)

log("=== Job Tracker Smart v2 starting ===")

# ── Google API client ──────────────────────────────────────────────────────────
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_gmail_service():
    creds = Credentials.from_authorized_user_file(GMAIL_TOKEN)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)

def get_sheets_service():
    creds = Credentials.from_authorized_user_file(GMAIL_TOKEN)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)

# ── MSN token refresh ──────────────────────────────────────────────────────────
def get_msn_token():
    with open(MSN_TOKEN) as f:
        td = json.load(f)
    # refresh
    data = urllib.parse.urlencode({
        "client_id": MSN_CLIENT_ID,
        "grant_type": "refresh_token",
        "refresh_token": td["refresh_token"],
        "scope": "Mail.Read offline_access"
    }).encode()
    req = urllib.request.Request(
        "https://login.microsoftonline.com/consumers/oauth2/v2.0/token",
        data=data, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            new = json.load(r)
        td.update(new)
        with open(MSN_TOKEN, "w") as f:
            json.dump(td, f)
        log(f"MSN token refreshed, expires_in={new.get('expires_in')}")
        return td["access_token"]
    except Exception as e:
        log(f"MSN token refresh failed: {e}")
        return td.get("access_token")

# ── helpers ────────────────────────────────────────────────────────────────────
FALSE_POS_DOMAINS = {
    "hdbfs.com","sbicard.com","jio.com","marutidealers.com",
    "starterstory.com","zintro.com","ebay.com","paypal.com",
    "bankofamerica.com","chase.com","amazon.com"
}
JOB_SENDER_KEYWORDS = [
    "greenhouse","lever","workday","icims","smartrecruiters","taleo",
    "jobvite","ashby","linkedin","google","microsoft","nvidia","meta",
    "amazon","apple","stripe","uber","airbnb","netflix","salesforce",
    "career","talent","recruit","hire","hiring","jobs"
]
JOB_SUBJECT_KEYWORDS = [
    "apply","applied","application","position","role","opportunity",
    "interview","offer","candidate","hiring","assessment",
    "thank you for your interest","thanks for applying","thank you for applying"
]

def sender_domain(from_hdr: str) -> str:
    m = re.search(r'@([\w.\-]+)', from_hdr or "")
    return m.group(1).lower() if m else ""

def passes_prefilter(from_hdr: str, subject: str) -> bool:
    dom = sender_domain(from_hdr)
    if dom in FALSE_POS_DOMAINS:
        return False
    from_lc = (from_hdr or "").lower()
    subj_lc = (subject or "").lower()
    sender_ok = any(k in from_lc for k in JOB_SENDER_KEYWORDS)
    subject_ok = any(k in subj_lc for k in JOB_SUBJECT_KEYWORDS)
    return sender_ok or subject_ok

def decode_body(part) -> str:
    """Recursively decode email body parts."""
    text = ""
    mime = part.get("mimeType","")
    if mime in ("text/plain","text/html"):
        data = part.get("body",{}).get("data","")
        if data:
            try:
                raw = base64.urlsafe_b64decode(data + "==")
                text = raw.decode("utf-8","replace")
            except Exception:
                pass
    for sub in part.get("parts",[]):
        text += decode_body(sub)
    return text

def get_header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""

def parse_date(ts_ms) -> datetime.date:
    try:
        return datetime.datetime.fromtimestamp(int(ts_ms)/1000).date()
    except Exception:
        return TODAY

def extract_job_id(text: str) -> str:
    patterns = [
        r'[Jj]ob\s*[Ii][Dd]\s*[:#]?\s*([A-Z0-9\-]{4,20})',
        r'[Rr]eq\s*(?:uisition)?\s*[Ii][Dd]?\s*[:#]?\s*([A-Z0-9\-]{4,20})',
        r'[Rr]eq\s*#\s*([A-Z0-9\-]{4,20})',
        r'gh_jid=(\d+)',
        r'jobId=([A-Z0-9\-]{4,20})',
        r'/jobs?/([0-9]{4,12})\b',
        r'/posting/([a-f0-9\-]{8,})\b',
        r'req_id=([A-Z0-9\-]{4,20})',
        r'(\bR-?\d{5,}\b)',
        r'(\bJR\d{5,}\b)',
        r'REF-(\d{4,})',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)
    return ""

def extract_position(subject: str, body: str) -> str:
    patterns = [
        r'applied for\s+(?:the\s+)?(.+?)(?:\s+at\s+|\s+role|\s+position|\s+job|\.|$)',
        r'application for\s+(?:the\s+)?(.+?)(?:\s+at\s+|\s+position|\s+role|\.|$)',
        r'for the\s+(.+?)\s+(?:role|position|opportunity)\b',
        r'the\s+(.+?)\s+(?:role|position)\s+at\b',
        r'applying for\s+(?:the\s+)?(.+?)(?:\s+at|\s+role|\s+position|\.|$)',
        r'your application.*?(?:for\s+(?:the\s+)?)(.+?)(?:\s+at\s+|\s+position|\.|$)',
        r'position:\s*(.+)',
        r'role:\s*(.+)',
    ]
    for text in [subject, body[:2000]]:
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                title = m.group(1).strip()
                title = re.sub(r'\s+', ' ', title)
                if 3 < len(title) < 100:
                    return title
    # fallback: strip company name from subject
    subj = re.sub(r'\b(Thank you|Thanks|Application|Received|Confirmation)\b', '', subject, flags=re.IGNORECASE)
    subj = subj.strip(" -–|:")
    if 3 < len(subj) < 80:
        return subj
    return ""

def extract_company(from_hdr: str, body: str) -> str:
    dom = sender_domain(from_hdr)
    # well-known ATS — try to get company from body
    ats = {"greenhouse-mail.io","lever.co","greenhouse.io","myworkdayjobs.com",
           "workday.com","icims.com","smartrecruiters.com","taleo.net","jobvite.com","ashbyhq.com"}
    if dom in ats or any(a in dom for a in ats):
        # look for "at <Company>" or "with <Company>"
        for p in [r'at\s+([A-Z][A-Za-z0-9\s&.,]+?)(?:\.|,|\s+is|\s+we|\s+our|\n)', 
                  r'with\s+([A-Z][A-Za-z0-9\s&.,]+?)(?:\.|,|\s+is|\s+we|\s+our|\n)',
                  r'([A-Z][A-Za-z0-9\s&,]+?)\s+(?:team|careers|recruiting|talent)']:
            m = re.search(p, body[:1500])
            if m:
                c = m.group(1).strip()
                if 2 < len(c) < 50:
                    return c
    # derive from domain
    parts = dom.split(".")
    if len(parts) >= 2:
        name = parts[-2]
        # strip common suffixes
        name = re.sub(r'(mail|no-?reply|careers|jobs|hr|talent|recruit)','', name)
        if name:
            return name.replace("-"," ").title()
    return dom

def platform_from(from_hdr: str) -> str:
    dom = sender_domain(from_hdr)
    mapping = {
        "greenhouse-mail.io": "Greenhouse",
        "greenhouse.io": "Greenhouse",
        "lever.co": "Lever",
        "myworkdayjobs.com": "Workday",
        "workday.com": "Workday",
        "icims.com": "iCIMS",
        "smartrecruiters.com": "SmartRecruiters",
        "taleo.net": "Taleo",
        "jobvite.com": "Jobvite",
        "ashbyhq.com": "Ashby",
        "linkedin.com": "LinkedIn",
    }
    for k, v in mapping.items():
        if k in dom:
            return v
    if "google" in dom:
        return "Google Careers"
    if "microsoft" in dom:
        return "Microsoft Careers"
    return "Direct/Company Website"

def determine_status(texts: list) -> str:
    """texts = list of body strings from all messages in thread (newest last)."""
    interview_kws = ["hiring assessment","interview","phone screen","next round",
                     "technical screen","next steps","schedule a call","video call",
                     "we'd like to speak","we would like to speak","move forward",
                     "moving forward with you","selected to move","advance to"]
    reject_kws = ["not move forward","not moving forward","regret to inform",
                  "decided to pursue","not selected","unfortunately we","we will not",
                  "won't be moving","not a match","other candidates","not proceed",
                  "no longer considering","position has been filled","closed"]
    review_kws = ["under review","reviewing your","being considered","in review",
                  "review process","currently reviewing"]

    combined = " ".join(texts).lower()
    if any(k in combined for k in interview_kws):
        return "Interview Scheduled"
    if any(k in combined for k in reject_kws):
        return "Rejected"
    if any(k in combined for k in review_kws):
        return "Under Review"
    return "Applied"

def extract_notes(body: str, subject: str) -> str:
    notes = []
    # recruiter
    for p in [r'(?:recruiter|hiring manager|talent|contact)[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)',
              r'Best,\s*\n([A-Z][a-z]+ [A-Z][a-z]+)',
              r'Regards,\s*\n([A-Z][a-z]+ [A-Z][a-z]+)']:
        m = re.search(p, body)
        if m:
            notes.append(f"Recruiter: {m.group(1).strip()}")
            break
    # salary
    for p in [r'\$[\d,]+(?:K|k)?(?:\s*[-–]\s*\$[\d,]+(?:K|k)?)?',
              r'[\d,]+K?\s*(?:USD|per year|annually)']:
        m = re.search(p, body)
        if m:
            notes.append(f"Salary: {m.group(0).strip()}")
            break
    # location
    for p in [r'(?:location|office)[:\s]+([A-Z][A-Za-z\s,]+(?:Remote|CA|NY|WA|TX|MA|IL)?)',
              r'\b(Remote|Hybrid|On-site)\b']:
        m = re.search(p, body, re.IGNORECASE)
        if m:
            notes.append(f"Location: {m.group(1).strip()}")
            break
    # assessment deadline
    m = re.search(r'(?:deadline|complete by|due by)[:\s]+(.{5,40})', body, re.IGNORECASE)
    if m:
        notes.append(f"Deadline: {m.group(1).strip()}")
    return "; ".join(notes)[:200]

# ── Gmail scanning ─────────────────────────────────────────────────────────────
GMAIL_QUERIES = [
    '"Thanks for applying" after:2025/11/01 before:2026/02/18',
    '"Thank you for applying" after:2025/11/01 before:2026/02/18',
    '"Thank you for your interest" after:2025/11/01 before:2026/02/18',
    '"Thanks for your interest" after:2025/11/01 before:2026/02/18',
    '"You applied for" after:2025/11/01 before:2026/02/18',
    '"Your application was sent" after:2025/11/01 before:2026/02/18',
    '"application received" after:2025/11/01 before:2026/02/18',
    'from:greenhouse.io after:2025/11/01 before:2026/02/18',
    'from:greenhouse-mail.io after:2025/11/01 before:2026/02/18',
    'from:lever.co after:2025/11/01 before:2026/02/18',
    'from:myworkdayjobs.com after:2025/11/01 before:2026/02/18',
    'from:workday.com after:2025/11/01 before:2026/02/18',
    'from:icims.com after:2025/11/01 before:2026/02/18',
    'from:smartrecruiters.com after:2025/11/01 before:2026/02/18',
    'from:taleo.net after:2025/11/01 before:2026/02/18',
    'from:jobvite.com after:2025/11/01 before:2026/02/18',
    'from:ashbyhq.com after:2025/11/01 before:2026/02/18',
    'from:no-reply@us.greenhouse-mail.io after:2025/11/01 before:2026/02/18',
    '(from:noreply@google.com) ("applying" OR "application") after:2025/11/01 before:2026/02/18',
    '(from:careers OR from:talent OR from:recruiting) ("applied" OR "application" OR "position") after:2025/11/01 before:2026/02/18',
]

def gmail_collect_threads(svc):
    thread_ids = set()
    for q in GMAIL_QUERIES:
        log(f"  Gmail query: {q[:70]}...")
        page_token = None
        page = 0
        while True:
            try:
                kwargs = dict(userId="me", q=q, maxResults=500)
                if page_token:
                    kwargs["pageToken"] = page_token
                resp = svc.users().threads().list(**kwargs).execute()
            except Exception as e:
                log(f"    Error: {e}")
                break
            threads = resp.get("threads", [])
            for t in threads:
                thread_ids.add(t["id"])
            page_token = resp.get("nextPageToken")
            page += 1
            log(f"    → page {page}: {len(threads)} threads (total unique: {len(thread_ids)})")
            if not page_token or page >= 5:  # cap at 5 pages per query
                break
        time.sleep(0.1)
    return thread_ids

def gmail_process_threads(svc, thread_ids):
    apps = []
    total = len(thread_ids)
    log(f"Processing {total} unique Gmail threads...")
    
    for i, tid in enumerate(thread_ids):
        if i % 20 == 0:
            log(f"  Progress: {i}/{total} threads processed, {len(apps)} apps found")
        
        try:
            # Step 1: metadata only (fast)
            meta = svc.users().threads().get(
                userId="me", id=tid, format="metadata",
                metadataHeaders=["From","Subject","Date"]
            ).execute()
        except Exception as e:
            log(f"  Thread {tid} meta error: {e}")
            continue

        msgs = meta.get("messages", [])
        if not msgs:
            continue

        first_msg = msgs[0]
        headers = first_msg.get("payload", {}).get("headers", [])
        from_hdr = get_header(headers, "From")
        subject  = get_header(headers, "Subject")

        # Pre-filter check
        if not passes_prefilter(from_hdr, subject):
            continue

        # Step 2: fetch full thread for accepted threads
        try:
            full = svc.users().threads().get(
                userId="me", id=tid, format="full"
            ).execute()
        except Exception as e:
            log(f"  Thread {tid} full fetch error: {e}")
            continue

        full_msgs = full.get("messages", [])
        if not full_msgs:
            continue

        # Extract dates
        first_hdrs = full_msgs[0].get("payload", {}).get("headers", [])
        last_hdrs  = full_msgs[-1].get("payload", {}).get("headers", [])
        ts_first   = full_msgs[0].get("internalDate", "0")
        ts_last    = full_msgs[-1].get("internalDate", "0")
        date_applied = parse_date(ts_first)
        date_updated = parse_date(ts_last)

        from_hdr = get_header(first_hdrs, "From")
        subject  = get_header(first_hdrs, "Subject")

        # Collect all bodies
        bodies = []
        for msg in full_msgs:
            payload = msg.get("payload", {})
            body = decode_body(payload)
            if body:
                bodies.append(body)

        combined_body = "\n".join(bodies)

        company  = extract_company(from_hdr, combined_body)
        position = extract_position(subject, combined_body)
        job_id   = extract_job_id(combined_body + " " + subject)
        platform = platform_from(from_hdr)
        status   = determine_status(bodies)
        notes    = extract_notes(combined_body, subject)
        days     = (TODAY - date_applied).days
        followup = "YES" if status in ("Applied", "No Response") and days > 14 else "NO"

        apps.append({
            "job_id":       job_id,
            "company":      company,
            "position":     position,
            "date_applied": date_applied.strftime("%m/%d/%Y"),
            "platform":     platform,
            "email_acct":   "gmail",
            "status":       status,
            "last_update":  date_updated.strftime("%m/%d/%Y"),
            "followup":     followup,
            "days":         days,
            "notes":        notes,
            "_thread_id":   tid,
            "_from":        from_hdr,
            "_subject":     subject,
            "_date_raw":    date_applied.isoformat(),
        })
        time.sleep(0.05)

    log(f"Gmail done: {len(apps)} applications extracted from {total} threads")
    return apps

# ── MSN scanning ───────────────────────────────────────────────────────────────
MSN_SEARCH_PHRASES = [
    "Thanks for applying",
    "Thank you for applying",
    "Thank you for your interest",
    "Thanks for your interest",
    "application received",
    "You applied for",
    "Your application was sent",
    "application confirmation",
]

def msn_api(access_token, path, params=None):
    url = "https://graph.microsoft.com/v1.0" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8","replace")
        log(f"  MSN API error {e.code}: {body[:200]}")
        return {}

def msn_collect_messages(access_token):
    """Collect messages from MSN using search phrases."""
    msg_ids = {}  # id -> message data
    conv_ids = {}  # conversationId -> list of msg ids

    for phrase in MSN_SEARCH_PHRASES:
        log(f"  MSN search: \"{phrase}\"")
        # Use $search with OData filter
        params = {
            "$search": f'"{phrase}"',
            "$select": "id,subject,from,receivedDateTime,conversationId,bodyPreview",
            "$top": "50",
            "$filter": "receivedDateTime ge 2025-11-01T00:00:00Z"
        }
        # Note: $search and $filter can't both be used; use $search only
        params2 = {
            "$search": f'"{phrase}"',
            "$select": "id,subject,from,receivedDateTime,conversationId,bodyPreview",
            "$top": "50",
        }
        data = msn_api(access_token, "/me/messages", params2)
        msgs = data.get("value", [])
        log(f"    → {len(msgs)} results")
        for m in msgs:
            recv = m.get("receivedDateTime","")
            if recv and recv < "2025-11-01":
                continue
            mid = m["id"]
            if mid not in msg_ids:
                msg_ids[mid] = m
                cid = m.get("conversationId","")
                if cid:
                    conv_ids.setdefault(cid, []).append(mid)
        time.sleep(0.2)

    log(f"MSN: {len(msg_ids)} unique messages, {len(conv_ids)} conversations")
    return msg_ids, conv_ids

def msn_process(access_token, msg_ids, conv_ids):
    apps = []
    processed_convs = set()

    for mid, msg in msg_ids.items():
        from_info = msg.get("from", {}).get("emailAddress", {})
        from_email = from_info.get("address", "")
        from_name  = from_info.get("name", "")
        from_hdr   = f"{from_name} <{from_email}>"
        subject    = msg.get("subject", "")
        recv_dt    = msg.get("receivedDateTime", "")
        body_prev  = msg.get("bodyPreview", "")
        conv_id    = msg.get("conversationId", "")

        if not passes_prefilter(from_hdr, subject):
            continue

        # deduplicate by conversation
        if conv_id and conv_id in processed_convs:
            continue
        if conv_id:
            processed_convs.add(conv_id)

        # Fetch full message body
        try:
            full = msn_api(access_token, f"/me/messages/{mid}",
                          {"$select": "id,subject,from,receivedDateTime,body,conversationId"})
            body_text = full.get("body", {}).get("content", body_prev)
        except Exception as e:
            log(f"  MSN full msg error: {e}")
            body_text = body_prev

        # If we have a conversationId, try to get other messages in that conv
        conv_bodies = [body_text]
        last_dt = recv_dt
        if conv_id and conv_id in conv_ids:
            for other_mid in conv_ids[conv_id]:
                if other_mid == mid:
                    continue
                other = msg_ids.get(other_mid, {})
                other_dt = other.get("receivedDateTime","")
                if other_dt > last_dt:
                    last_dt = other_dt
                conv_bodies.append(other.get("bodyPreview",""))

        # Parse date
        try:
            date_applied = datetime.datetime.fromisoformat(recv_dt.replace("Z","+00:00")).date()
        except Exception:
            date_applied = TODAY
        try:
            date_updated = datetime.datetime.fromisoformat(last_dt.replace("Z","+00:00")).date()
        except Exception:
            date_updated = date_applied

        combined_body = "\n".join(conv_bodies)
        company  = extract_company(from_hdr, combined_body)
        position = extract_position(subject, combined_body)
        job_id   = extract_job_id(combined_body + " " + subject)
        platform = platform_from(from_hdr)
        status   = determine_status(conv_bodies)
        notes    = extract_notes(combined_body, subject)
        days     = (TODAY - date_applied).days
        followup = "YES" if status in ("Applied", "No Response") and days > 14 else "NO"

        apps.append({
            "job_id":       job_id,
            "company":      company,
            "position":     position,
            "date_applied": date_applied.strftime("%m/%d/%Y"),
            "platform":     platform,
            "email_acct":   "msn",
            "status":       status,
            "last_update":  date_updated.strftime("%m/%d/%Y"),
            "followup":     followup,
            "days":         days,
            "notes":        notes,
            "_conv_id":     conv_id,
            "_from":        from_hdr,
            "_subject":     subject,
            "_date_raw":    date_applied.isoformat(),
        })
        time.sleep(0.05)

    log(f"MSN done: {len(apps)} applications extracted")
    return apps

# ── Deduplication ──────────────────────────────────────────────────────────────
def dedup(apps):
    seen = {}  # key -> app
    result = []

    for app in apps:
        jid = app["job_id"].strip()
        co  = app["company"].strip().lower()[:30]
        pos = app["position"].strip().lower()[:30]
        date_raw = app.get("_date_raw","")

        if jid and co:
            key = f"jid:{jid}:{co}"
        else:
            # fuzzy: company + position + date ±3 days
            try:
                d = datetime.date.fromisoformat(date_raw)
                # round to week
                d_key = d.strftime("%Y-W%W")
            except Exception:
                d_key = date_raw
            key = f"cp:{co[:20]}:{pos[:20]}:{d_key}"

        if key in seen:
            # merge email accounts
            existing = seen[key]
            if existing["email_acct"] != app["email_acct"]:
                existing["email_acct"] = "gmail+msn"
            # keep "better" status
            priority = {"Interview Scheduled":4,"Under Review":3,"Rejected":2,"Applied":1}
            if priority.get(app["status"],0) > priority.get(existing["status"],0):
                existing["status"] = app["status"]
                existing["last_update"] = app["last_update"]
                existing["notes"] = app["notes"]
        else:
            seen[key] = app
            result.append(app)

    log(f"After dedup: {len(result)} unique applications (from {len(apps)} total)")
    return result

# ── Sort ───────────────────────────────────────────────────────────────────────
def sort_apps(apps):
    def sort_key(a):
        try:
            return datetime.datetime.strptime(a["date_applied"], "%m/%d/%Y")
        except Exception:
            return datetime.datetime.min
    return sorted(apps, key=sort_key, reverse=True)

# ── Write to sheet ─────────────────────────────────────────────────────────────
def write_to_sheet(apps):
    svc = get_sheets_service()
    sh  = svc.spreadsheets()

    # Get spreadsheet metadata to find correct sheetId
    meta = sh.get(spreadsheetId=SHEET_ID).execute()
    sheets = meta.get("sheets", [])
    app_sheet_id = None
    app_sheet_name = None
    for s in sheets:
        sp = s.get("properties", {})
        title = sp.get("title","")
        if "application" in title.lower() or "app" in title.lower():
            app_sheet_id   = sp["sheetId"]
            app_sheet_name = title
            break
    if app_sheet_id is None:
        # use first sheet
        sp = sheets[0]["properties"]
        app_sheet_id   = sp["sheetId"]
        app_sheet_name = sp["title"]
    log(f"Target sheet: '{app_sheet_name}' (sheetId={app_sheet_id})")

    # Clear existing data
    sh.values().clear(spreadsheetId=SHEET_ID, range=f"{app_sheet_name}!A:K").execute()
    log("Sheet cleared.")

    # Build rows
    headers = [
        "Job ID","Company Name","Position Title","Date Applied",
        "Source/Platform","Email Account","Current Status","Last Update Date",
        "Follow-Up Needed","Days Since Applied","Notes"
    ]
    rows = [headers]
    for app in apps:
        rows.append([
            app["job_id"],
            app["company"],
            app["position"],
            app["date_applied"],
            app["platform"],
            app["email_acct"],
            app["status"],
            app["last_update"],
            app["followup"],
            str(app["days"]),
            app["notes"],
        ])

    # Write data
    sh.values().update(
        spreadsheetId=SHEET_ID,
        range=f"{app_sheet_name}!A1",
        valueInputOption="RAW",
        body={"values": rows}
    ).execute()
    log(f"Wrote {len(rows)} rows (1 header + {len(apps)} apps) to sheet.")

    # ── Formatting ──────────────────────────────────────────────────────────────
    def color(hex_str):
        hex_str = hex_str.lstrip("#")
        r = int(hex_str[0:2],16)/255
        g = int(hex_str[2:4],16)/255
        b = int(hex_str[4:6],16)/255
        return {"red":r,"green":g,"blue":b}

    requests = []

    # Header row format
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": app_sheet_id,
                "startRowIndex": 0, "endRowIndex": 1,
                "startColumnIndex": 0, "endColumnIndex": 11
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": color("1a5276"),
                    "textFormat": {"foregroundColor": color("FFFFFF"), "bold": True, "fontSize": 11},
                    "horizontalAlignment": "CENTER"
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
        }
    })

    # Freeze header
    requests.append({
        "updateSheetProperties": {
            "properties": {"sheetId": app_sheet_id, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount"
        }
    })

    # Auto-resize columns
    requests.append({
        "autoResizeDimensions": {
            "dimensions": {
                "sheetId": app_sheet_id,
                "dimension": "COLUMNS",
                "startIndex": 0, "endIndex": 11
            }
        }
    })

    # Row coloring by status
    status_colors = {
        "Rejected":           "E0E0E0",
        "Interview Scheduled":"C8E6C9",
    }
    for row_idx, app in enumerate(apps, start=1):
        row_color = None
        if app["followup"] == "YES":
            row_color = "FFF9C4"
        if app["status"] in status_colors:
            row_color = status_colors[app["status"]]  # status overrides followup color

        if row_color:
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": app_sheet_id,
                        "startRowIndex": row_idx, "endRowIndex": row_idx+1,
                        "startColumnIndex": 0, "endColumnIndex": 11
                    },
                    "cell": {
                        "userEnteredFormat": {"backgroundColor": color(row_color)}
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            })

    # Apply all formatting in one batch
    if requests:
        sh.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": requests}).execute()
        log("Formatting applied.")

    return len(apps)

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    all_apps = []

    # ── Gmail ──────────────────────────────────────────────────────────────────
    log("=== GMAIL SCAN ===")
    try:
        gmail_svc = get_gmail_service()
        thread_ids = gmail_collect_threads(gmail_svc)
        log(f"Collected {len(thread_ids)} unique thread IDs from Gmail")
        gmail_apps = gmail_process_threads(gmail_svc, thread_ids)
        all_apps.extend(gmail_apps)
    except Exception as e:
        log(f"Gmail scan error: {e}")
        traceback.print_exc()

    # ── MSN ────────────────────────────────────────────────────────────────────
    log("=== MSN SCAN ===")
    try:
        access_token = get_msn_token()
        msg_ids, conv_ids = msn_collect_messages(access_token)
        msn_apps = msn_process(access_token, msg_ids, conv_ids)
        all_apps.extend(msn_apps)
    except Exception as e:
        log(f"MSN scan error: {e}")
        traceback.print_exc()

    log(f"=== TOTAL BEFORE DEDUP: {len(all_apps)} ===")

    # ── Dedup + sort ───────────────────────────────────────────────────────────
    apps = dedup(all_apps)
    apps = sort_apps(apps)

    # ── Status breakdown ───────────────────────────────────────────────────────
    status_counts = {}
    for app in apps:
        s = app["status"]
        status_counts[s] = status_counts.get(s, 0) + 1
    log(f"Status breakdown: {status_counts}")

    # ── Write sheet ────────────────────────────────────────────────────────────
    log("=== WRITING TO GOOGLE SHEET ===")
    try:
        count = write_to_sheet(apps)
        log(f"Sheet updated with {count} applications.")
    except Exception as e:
        log(f"Sheet write error: {e}")
        traceback.print_exc()

    # ── Save state ─────────────────────────────────────────────────────────────
    state = {
        "sheet_id": SHEET_ID,
        "last_scan": "2026-02-17",
        "scan_type": "historical",
        "total": len(apps),
        "status_breakdown": status_counts,
        "applications": apps
    }
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    log(f"State saved to {STATE_FILE}")

    # ── Final summary ──────────────────────────────────────────────────────────
    log("=== COMPLETE ===")
    log(f"Total applications: {len(apps)}")
    for s, n in sorted(status_counts.items(), key=lambda x: -x[1]):
        log(f"  {s}: {n}")
    log(f"Sheet URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
    print("\n" + "="*60)
    print(f"✅ JOB TRACKER COMPLETE")
    print(f"   Total applications: {len(apps)}")
    for s, n in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"   {s}: {n}")
    print(f"   Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
    print("="*60)

if __name__ == "__main__":
    main()
