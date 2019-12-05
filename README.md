# Mimecast

## Migrated to Python 3.6 +

Supports the following endpoints to query:

get_siem_logs <br>
get_ttp_urls <br>
get_auth_logs <br>

## Documentation:

https://www.mimecast.com/tech-connect/documentation/endpoint-reference/

## Geting Started:
1. Edit `configuration.py` to change Mimecast API details and select approriate requirements <br>
2. Create the following files in `logs/`: <br>
```
   hash_file
   audit_events
   ttp_events
```
3. Run `run.py` to start ingesting - program is threaded so each source selected in `configuration.py` will run simultaneously.

## Supported Output:

Define the type of output you want within the `configuration.py` file.

* Supports sending JSON and | delimited messages to UDP syslog
* Output to file only

You can use a SIEM product to ingest these events easily.

## Troubleshooting - contributions welcome!

SSL / connectivity to API issues: https://stackoverflow.com/questions/56858075/pulling-mimecast-logs-with-python

## Contact

Joshua Smeda <br>
https://www.linkedin.com/in/joshua-smeda-7b9102103/
