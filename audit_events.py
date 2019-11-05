	
import base64
import hashlib
import hmac
import uuid
import datetime
import requests
 
# Setup required variables
base_url = "https://xx-api.mimecast.com"
uri = "/api/audit/get-audit-events"
url = base_url + uri
access_key = "YOUR ACCESS KEY"
secret_key = "YOUR SECRET KEY"
app_id = "YOUR APPLICATION ID"
app_key = "YOUR APPLICATION KEY"
 
# Generate request header values
request_id = str(uuid.uuid4())
hdr_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S") + " UTC"
 
# Create the HMAC SHA1 of the Base64 decoded secret key for the Authorization header
hmac_sha1 = hmac.new(secret_key.decode("base64"), ':'.join([hdr_date, request_id, uri, app_key]),
                  digestmod=hashlib.sha1).digest()
 
# Use the HMAC SHA1 value to sign the hdrDate + ":" requestId + ":" + URI + ":" + appkey
sig = base64.encodestring(hmac_sha1).rstrip()
 
# Create request headers
headers = {
    'Authorization': 'MC ' + access_key + ':' + sig,
    'x-mc-app-id': app_id,
    'x-mc-date': hdr_date,
    'x-mc-req-id': request_id,
    'Content-Type': 'application/json'
}
 
payload = {
        'data': [
            {
                'startDateTime': 'Date String',
                'endDateTime': 'Date String',
                'query': 'String',
                'categories': [
                    'String'
                ]
            }
        ]
    }
 
r = requests.post(url=url, headers=headers, data=str(payload))
 
print r.text