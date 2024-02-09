# Mimecast


Supports the following Mimecast endpoints:

* get-siem-logs
* get-audit-events

## Documentation:

https://www.mimecast.com/tech-connect/documentation/endpoint-reference/

## Getting Started:
1. Edit `Config.py` to change Mimecast API details and select approriate requirements. The auth creds are required (you will need to generate a API user via the console) - https://www.mimecast.com/tech-connect/documentation <br>
2. The script will automatically create the directories defined in 'configuration.py` for hashing / logging
3. Run `run.py` to start ingesting - program is threaded so each source configured in `Config.py` will run simultaneously.

## Output:

Auth and SIEM events written locally, sent to AWS S3, and then removed from local storage.

You can use a SIEM product to ingest these events easily (since it's JSON). Examples include, SIEM Monster, Splunk, ManageEngine, ELK, QRadar, etc.

## Troubleshooting

Connectivity / SSL issues when connecting to the Mimecast API: https://stackoverflow.com/questions/56858075/pulling-mimecast-logs-with-python

If you are experiencing high CPU usage - increase the interval time in `Config.py` until a point where the issue no longer occurs.

## Attributions

Forked from https://github.com/JoshuaSmeda/mimecast_log_collector