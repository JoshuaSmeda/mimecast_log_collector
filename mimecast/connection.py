import json
import requests
import base64
import uuid
import hashlib
import hmac
import time
import mimecast.Config

from mimecast.logger import log, get_hdr_date


class Mimecast():
    def __init__(self, event_type):
        self.event_type = event_type
        self.Config = mimecast.Config.Config()

    def create_signature(self, data_to_sign: str, secret_key: str, encoding='utf-8'):
        secret_key = secret_key.encode(encoding)
        data_to_sign = data_to_sign.encode(encoding)
        secret_key = base64.b64decode(secret_key)
        digest = hmac.new(secret_key, data_to_sign, digestmod=hashlib.sha1).digest()  # still bytes
        digest_b64 = base64.b64encode(digest)  # bytes again
        return digest_b64.decode(encoding)  # that's now str

    def get_base_url(self, email_address):
        # Create post body for request
        post_body = dict()
        post_body['data'] = [{}]
        post_body['data'][0]['emailAddress'] = email_address

        # Create variables required for request headers
        request_id = str(uuid.uuid4())
        request_date = get_hdr_date()
        headers = {'x-mc-app-id': self.Config.get_app_id(), 'x-mc-req-id': request_id, 'x-mc-date': request_date}
        # Send request to API
        log.debug('Sending request to https://api.mimecast.com/api/discover-authentication with request ID: %s' % (request_id))
        try:
            r = requests.post(url='https://api.mimecast.com/api/login/discover-authentication', data=json.dumps(post_body), headers=headers, verify=False)

            # Handle Rate Limiting
            if r.status_code == 429:
                rate_limit = (int(r.headers['X-RateLimit-Reset'])/1000) % 60
                time.sleep(rate_limit * 20)
        except Exception as e:
            log.error('Unexpected error getting base url. Cannot continue.' + str(e))
            quit()

        # Handle error from API
        if r.status_code != 200:
            log.error('Request returned with status code: ' + str(r.status_code) + ', response body: ' + r.text + '. Cannot continue.')
            quit()

        # Load response body as JSON
        resp_data = json.loads(r.text)

        # Look for api key in region region object to get base url
        if 'region' in resp_data["data"][0]:
            base_url = resp_data["data"][0]["region"]["api"].split('//')
            base_url = base_url[1]
        else:
            # Handle no region found, likely the email address was entered incorrectly
            log.error('No region information returned from API, please check the supplied email address in configuration.py. Cannot continue')
            quit()

        return base_url

    def post_request(self, base_url, uri, post_body, access_key, secret_key):
        # Create variables required for request headers
        request_id = str(uuid.uuid4())
        request_date = get_hdr_date()
        signature = 'MC ' + access_key + ':' + self.create_signature(':'.join([request_date, request_id, uri, self.Config.get_app_key()]), secret_key)
        headers = {'Authorization': signature, 'x-mc-app-id': self.Config.get_app_id(), 'x-mc-req-id': request_id, 'x-mc-date': request_date}

        try:
            # Send request to API
            log.debug('Sending request to https://' + base_url + self.event_type + ' with request Id: ' + request_id)
            r = requests.post(url='https://' + base_url + uri, data=json.dumps(post_body), headers=headers, verify=False)

        # Handle errors on client side
        except Exception as e:
            log.error('Unexpected error connecting to API. Exception: ' + str(e))
            return 'error'

        # Handle errors from API
        if r.status_code != 200:
            log.error('Request to ' + uri + ' with , request id: ' + request_id + ' returned with status code: ' + str(r.status_code) + ', response body: ' + r.text)

        # Return response body and response headers
        return r.content, r.headers, r.status_code
