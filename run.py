import configuration
import time
import multiprocessing

# Import dependent functions
import ttp_events
#import siem_events
#import audit_events

source_list = []

for k, v in configuration.source_details.items():
    if v == True:
     #   print("%s is selected to be ingested" % (k))
        source_list.append(k)
    elif v == False:
        print("%s is selected to not be ingested" % (k))

print("\nStarting main process shortly in 10 seconds\n")
time.sleep(3)

"""
for i in source_list:
    print("Starting thread for %s" % (i))
    p = multiprocessing.Process(target=lambda: __import__(i))
    p.start()
"""