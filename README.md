# Mimecast


Supports the following Mimecast endpoints:

* get_siem_logs
* get_ttp_urls
* get_auth_logs

## Documentation:

https://www.mimecast.com/tech-connect/documentation/endpoint-reference/

## Getting Started:
1. Edit `Config.py` to change Mimecast API details and select approriate requirements. The auth creds are required (you will need to generate a API user via the console) - https://www.mimecast.com/tech-connect/documentation <br>
2. The script will automatically create the directories defined in 'configuration.py` for hashing / logging
```
   hash_file
   audit_events
   ttp_events
```
3. Run `run.py` to start ingesting - program is threaded so each source configured in `Config.py` will run simultaneously.

## Output:

The AUTH and TTP events are recorded, serialized into JSON and sent to syslog if configured. They are not recorded to file.
SIEM events are recorded to file and shipped to syslog, if configured.

You can use a SIEM product to ingest these events easily (since it's JSON). Examples include, SIEM Monster, Splunk, ManageEngine, ELK, QRadar, etc.

# AWS and S3
This update allows for copying the individual SIEM logs to an S3 bucket and for storing the Mimecast credential information and siem checkpoint in Parameter Store.

## Troubleshooting

Connectivity / SSL issues when connecting to the Mimecast API: https://stackoverflow.com/questions/56858075/pulling-mimecast-logs-with-python

If you are experiencing high CPU usage - increase the interval time in `Config.py` until a point where the issue no longer occurs.

## Attributions

Forked from https://github.com/JoshuaSmeda/mimecast_log_collector