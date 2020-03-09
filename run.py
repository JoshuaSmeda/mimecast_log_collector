import configuration
import time
import multiprocessing
import os

# Create logging directories
if not os.path.exists(configuration.logging_details['CHK_POINT_DIR']):
    os.makedirs(configuration.logging_details['CHK_POINT_DIR'])

if not os.path.exists(configuration.logging_details['LOG_FILE_PATH']):
    os.makedirs(configuration.logging_details['LOG_FILE_PATH'])

source_list = []

for k, v in configuration.source_details.items():
    if v == True:
        print("%s is selected to be ingested" % (k))
        source_list.append(k)
    else:
        print("%s is selected to not be ingested" % (k))

print("\nStarting main process shortly in 10 seconds\n")
time.sleep(3)

for i in source_list:
    p = multiprocessing.Process(target=lambda: __import__(i))
    p.start()
