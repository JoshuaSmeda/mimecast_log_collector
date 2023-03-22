# Mimecast

## History ##

This code was originally created by GitHub user JoshuaSmeda.  Unfortunately, as of 3/22/2023 (the 
inception of this fork), the original repository had not been touched for two years.  There were
some patches that had been submitted to the original developer, but it seemed that no response
was forthcoming.

## Motivation ##

**JSON parsing issue [FIXED]** - The TTP and Audit endpoints were returning JSON that was not being parsed correctly.
I documented this issue [here](https://github.com/JoshuaSmeda/mimecast_log_collector/issues/13)

**SIEM module large filecount per directory [FIXED]** - I didn't submit an issue for this one.  The issue is that
the script generates a large amount of files in the directory it points to for SIEM logs, so much so that normal
tools like `rm`, `ls`, etc. can't be used directly to manage them, and there's no built-in file rotation. 
My solution was to put the SIEM logs in directories based on date so that no one directory would have too many
files, then I created a log rotation script that would remove old logs.

**Compression** - Examples from Mimecast demonstrate how to implement compression when calling their APIs,
and they mention that using compression reduces the chance of getting rate limited.  I have a requirement
to implement this compression, so I will be working on that feature.

**Process mysteriously dies** - I've noticed this happening, but haven't identified a root cause

**No clean way to shut down process** - Unless you want to do `ps -ef | grep mime | awk '{print $2}' | xargs kill -9`
every time, it can be difficult to know how to shut down the process cleanly.

**No way to prevent multiple copies from running** - Running multiple copies of this script is obviously silly and 
counterproductive.  If you're running this from `cron`, you can't predict how long a run will be, so it can be
difficult to choose an interval that wouldn't collide with the next run.  

## Only Python 3 ##

Supports the following Mimecast endpoints:

```
get_siem_logs <br>
get_ttp_urls <br>
get_auth_logs <br>
```

## Documentation:

https://www.mimecast.com/tech-connect/documentation/endpoint-reference/

## Getting Started:
1. Edit `configuration.py` to change Mimecast API details and select approriate requirements. The auth creds are required (you will need to generate a API user via the console) - https://www.mimecast.com/tech-connect/documentation <br>
2. The script will automatically create the directories defined in 'configuration.py` for hashing / logging
```
   hash_file
   audit_events
   ttp_events
```
3. Run `run.py` to start ingesting - program is threaded so each source configured in `configuration.py` will run simultaneously.

## Output:

The auth and ttp events are recorded, serialized into json and sent to syslog if configured. They are not recorded to file.
SIEM events are recorded to file and shipped to syslog if configured

You can use a SIEM product to ingest these events easily since it's JSON. i.e SIEM Monster, Splunk, ManageEngine, Logstash, QRadar, etc.

## Troubleshooting - contributions welcome!

SSL / connectivity to API issues: https://stackoverflow.com/questions/56858075/pulling-mimecast-logs-with-python

If you are experiencing high CPU usage - increase the interval time in `configuration.py` until a point where the issue no longer occurs.

## Contact

Primary developer - ArkieCoder
Contact is via GitHub Issues
