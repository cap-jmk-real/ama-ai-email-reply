from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email import message_from_bytes
import re

# Scope to read Gmail messages
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials/credentials.json', SCOPES)
    creds = flow.run_local_server(port=8080)
    service = build('gmail', 'v1', credentials=creds)
    return service

def list_sent_messages(service, max_results=20):
    query = 'from:me'
    results = service.users().messages().list(
        userId='me', q=query, maxResults=max_results).execute()
    return results.get('messages', [])

def extract_own_message(text: str) -> str:
    reply_patterns = [
        r"(?i)^[-]+\s*Ursprüngliche Nachricht\s*[-]+",
        r"(?i)^Am .* schrieb .*:",
        r"(?i)^On .+ wrote:",
        r"(?i)^Von:.*",
        r"(?i)^From:.*",
        r"(?i)^Gesendet:.*",
        r"(?i)^Sent:.*",
        r"(?i)^To:.*",
        r"(?i)^An:.*",
        r"(?i)^Subject:.*",
        r"(?i)^>.*",
    ]

    earliest = len(text)
    for pattern in reply_patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            earliest = min(earliest, match.start())

    clean_text = text[:earliest].strip()
    return clean_text

def get_message_body(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
    msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
    mime_msg = message_from_bytes(msg_str)

    payload = mime_msg.get_payload()

    if isinstance(payload, list):
        for part in payload:
            if part.get_content_type() == 'text/plain':
                raw_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                return extract_own_message(raw_text)
        return None  # skip if no plain text part found
    elif isinstance(payload, str):
        return extract_own_message(payload)
    else:
        return None  # skip unsupported payload types

def main():
    service = authenticate_gmail()
    messages = list_sent_messages(service, max_results=500)

    print(f"Found {len(messages)} sent emails.")
    emails = []

    for msg in messages:
        try:
            body = get_message_body(service, msg['id'])
            if body:  # only add if not None
                emails.append(body)
        except Exception as e:
            print(f"Error reading message {msg['id']}: {e}")

    # Save cleaned messages
    with open("sent_emails_cleaned.txt", "w", encoding="utf-8") as f:
        for email in emails:
            f.write("--- EMAIL ---\n")
            f.write(email)
            f.write("\n\n")

    print(f"✅ Saved {len(emails)} cleaned emails to sent_emails_cleaned.txt")

if __name__ == '__main__':
    main()
