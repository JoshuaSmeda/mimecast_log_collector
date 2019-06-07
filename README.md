# Mimecast-log-collector
Collects Mimecast logs from Mimecast API (Can be pushed into a SIEM).

_Tested with Python 2_

<h2>How do I use this?</h2>
1. Place the script in a directory. `git clone`<br>
2. Replace authentication variables in the script with your Mimecast API details from your console. <br>
3. Run the script using `python` <br>

<br>
You can create a System V init script to run this script as a "service" and build health checking around this, as a example.
