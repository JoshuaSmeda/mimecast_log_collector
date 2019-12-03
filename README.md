# Mimecast

## Migrated to Python 3.6 +

Supports the following endpoints to query:

get_siem_logs <br>
get_ttp_urls <br>
get_auth_logs <br>

## Documentation:

https://www.mimecast.com/tech-connect/documentation/endpoint-reference/

## Get started:
1. Edit `configuration.py` to change Mimecast API details and select approriate requirements <br>
2. Create the following files in `logs/`: <br>
   touch audit_events <br>
   touch ttp_events <br>
3. Run `run.py` to start ingesting - program is threaded so each source selected in `configuration.py` will run simultaneously.

## Output:

Define the type of output you want within the `configuration.py` file.

* Supports sending JSON and | delimited messages to UDP syslog
* Output to file only

You can use a SIEM product to ingest these events easily.

## Troubleshoot - contributions welcome!

SSL / connectivity to API issues: https://stackoverflow.com/questions/56858075/pulling-mimecast-logs-with-python

## Contact

Joshua Smeda
https://www.linkedin.com/in/joshua-smeda-7b9102103/
