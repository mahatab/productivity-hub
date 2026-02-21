import sys, json, warnings, os
warnings.filterwarnings('ignore')
sys.path.insert(0, '/Users/mahatabrashid/Library/Python/3.9/lib/python/site-packages')

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PATH = os.path.expanduser('~/.clawdbot/gmail/token.json')

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

creds = get_creds()
service = build('sheets', 'v4', credentials=creds)

# Step 1: Create the spreadsheet
spreadsheet_body = {
    'properties': {
        'title': 'Mahatab - Job Applications Tracker'
    },
    'sheets': [{
        'properties': {
            'title': 'Applications',
            'gridProperties': {
                'rowCount': 1000,
                'columnCount': 10
            }
        }
    }]
}

spreadsheet = service.spreadsheets().create(body=spreadsheet_body).execute()
spreadsheet_id = spreadsheet['spreadsheetId']
sheet_id = spreadsheet['sheets'][0]['properties']['sheetId']

print(f"Created spreadsheet: {spreadsheet_id}")
print(f"Sheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")

# Step 2: Write headers
headers = [['Job ID', 'Company Name', 'Position Title', 'Date Applied (MM/DD/YYYY)',
             'Source/Platform', 'Current Status', 'Last Update Date',
             'Follow-Up Needed', 'Days Since Applied', 'Notes']]

service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id,
    range='Applications!A1:J1',
    valueInputOption='RAW',
    body={'values': headers}
).execute()

# Step 3: Apply formatting
requests = [
    # Freeze header row
    {
        'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'gridProperties': {
                    'frozenRowCount': 1
                }
            },
            'fields': 'gridProperties.frozenRowCount'
        }
    },
    # Bold + blue background + white text for header
    {
        'repeatCell': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': 0,
                'endRowIndex': 1,
                'startColumnIndex': 0,
                'endColumnIndex': 10
            },
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': {
                        'red': 0.102,
                        'green': 0.451,
                        'blue': 0.910
                    },
                    'textFormat': {
                        'bold': True,
                        'foregroundColor': {
                            'red': 1.0,
                            'green': 1.0,
                            'blue': 1.0
                        },
                        'fontSize': 11
                    },
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': 'MIDDLE'
                }
            },
            'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
        }
    },
    # Auto-resize all columns
    {
        'autoResizeDimensions': {
            'dimensions': {
                'sheetId': sheet_id,
                'dimension': 'COLUMNS',
                'startIndex': 0,
                'endIndex': 10
            }
        }
    },
    # Conditional formatting: Follow-Up Needed = YES → yellow (#FFF9C4)
    {
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': 1000,
                    'startColumnIndex': 0,
                    'endColumnIndex': 10
                }],
                'booleanRule': {
                    'condition': {
                        'type': 'CUSTOM_FORMULA',
                        'values': [{'userEnteredValue': '=$H2="YES"'}]
                    },
                    'format': {
                        'backgroundColor': {
                            'red': 1.0,
                            'green': 0.976,
                            'blue': 0.769
                        }
                    }
                }
            },
            'index': 0
        }
    },
    # Conditional formatting: Current Status = Rejected → gray (#E0E0E0)
    {
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': 1000,
                    'startColumnIndex': 0,
                    'endColumnIndex': 10
                }],
                'booleanRule': {
                    'condition': {
                        'type': 'CUSTOM_FORMULA',
                        'values': [{'userEnteredValue': '=$F2="Rejected"'}]
                    },
                    'format': {
                        'backgroundColor': {
                            'red': 0.878,
                            'green': 0.878,
                            'blue': 0.878
                        }
                    }
                }
            },
            'index': 1
        }
    },
    # Conditional formatting: Current Status = Interview Scheduled → green (#C8E6C9)
    {
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': 1000,
                    'startColumnIndex': 0,
                    'endColumnIndex': 10
                }],
                'booleanRule': {
                    'condition': {
                        'type': 'CUSTOM_FORMULA',
                        'values': [{'userEnteredValue': '=$F2="Interview Scheduled"'}]
                    },
                    'format': {
                        'backgroundColor': {
                            'red': 0.784,
                            'green': 0.902,
                            'blue': 0.788
                        }
                    }
                }
            },
            'index': 2
        }
    }
]

service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={'requests': requests}
).execute()

print("Formatting applied successfully.")

# Save spreadsheet ID
memory_path = '/Users/mahatabrashid/clawd/memory/job-tracker-sheet-id.txt'
with open(memory_path, 'w') as f:
    f.write(spreadsheet_id)

print(f"Spreadsheet ID saved to {memory_path}")
print(f"\nSHEET_URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
