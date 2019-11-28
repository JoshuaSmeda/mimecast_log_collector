import base64
import hashlib
import hmac
import uuid
import datetime
import requests

import configuration

# Setup required variables
base_url = "https://za-api.mimecast.com"
uri = "/api/audit/get-audit-events"
url = base_url + uri
access_key = "mYtOL3XZCOwG96BOiFTZRobmn0BUukXst5ZkLlSng4sBj3gSI7eO7AKdNiCk9xlCulNaFB4EEUVl76rXcsIemIClZcevBsB5iGaidDfpEPoWjVJuvNDLqAqGeB0OfU9Mm__xRFP6Q6FEcQuSNctWsQ"
secret_key = "qwU2U8W1tFViZlBdnDAiUinFJVHh/JW69NcugapHeRMccVvcyF+uzIgMMeXw7Q2gToIhs6mPaj9PfyMLxl5Vlg=="
app_id = "34107bdc-6f7f-4c1e-a313-5e3b224cd4e1"
app_key = "b58a89da-b5e3-4813-bc36-45f74a66e216"
 
# Generate request header values
request_id = str(uuid.uuid4())
request_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S") + " UTC"
 
# Create the HMAC SHA1 of the Base64 decoded secret key for the Authorization header
#hmac_sha1 = hmac.new(secret_key.decode("base64"), ':'.join([hdr_date, request_id, uri, app_key]), digestmod=hashlib.sha1).digest()
 
# Use the HMAC SHA1 value to sign the hdrDate + ":" requestId + ":" + URI + ":" + appkey
#sig = base64.encodestring(hmac_sha1).rstrip()


def create_signature(data_to_sign: str, secret_key: str, encoding='utf-8'):
    secret_key = secret_key.encode(encoding)
    data_to_sign = data_to_sign.encode(encoding)
    secret_key = base64.b64decode(secret_key)
    digest = hmac.new(secret_key, data_to_sign, digestmod=hashlib.sha1).digest()  # still bytes
    digest_b64 = base64.b64encode(digest)  # bytes again
    return digest_b64.decode(encoding)  # that's now str


signature = 'MC ' + access_key + ':' + create_signature(':'.join([request_date, request_id, uri, app_key]), secret_key)
print(signature)
headers = {'Authorization': signature, 'x-mc-app-id': app_id, 'x-mc-req-id': request_id, 'x-mc-date': request_date }

# Create request headers
"""
headers = {
    'Authorization': 'MC ' + access_key + ':' + sig,
    'x-mc-app-id': app_id,
    'x-mc-date': hdr_date,
    'x-mc-req-id': request_id,
    'Content-Type': 'application/json'
}
"""

payload = {
        'data': [
            {
                'startDateTime': '2018-12-03T10:15:30+0000',
                'endDateTime': '2019-12-03T10:15:30+0000',
            }
        ]
    }


r = requests.post(url=url, headers=headers, data=str(payload))


print(r.text)