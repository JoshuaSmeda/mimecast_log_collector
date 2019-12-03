import configuration
import time
import multiprocessing

source_list = []


for k, v in configuration.source_details.items():
    if v == True:
        print("%s is selected to be ingested" % (k))
        source_list.append(k)
    else:
        print("%s is selected to not be ingested" % (k))

print("\nStarting main process shortly in 10 seconds\n")
time.sleep(10)


for i in source_list:
    p = multiprocessing.Process(target=lambda: __import__(i))
    p.start()
