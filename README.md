# Mimecast-log-collector
Collects Mimecast logs from Mimecast API (Can be pushed into a SIEM).

_Tested with Python 2_

<h2>How do I use this?</h2>
1. Clone the repo <br>
2. Replace authentication variables in the script with your Mimecast API details from your console. <br>
3. Define the location where to store log files and checkpoint file.  <br>
4. Run the script.
<br>

On Linux, you can create a sysv init script to run this as a "service" - so it's easily to manage.
