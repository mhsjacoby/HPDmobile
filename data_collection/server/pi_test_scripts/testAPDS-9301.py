import hpd_sensors
import sys
from datetime import datetime
import os
import time

def main(id):
    size = 1
    test = hpd_sensors.HPD_APDS9301()
    d = {}
    while size <= 60:
        d[size] = test.read()
        print("Second: {}\tCurrent value: {}".format(size, d[size]))
        size += 1
        time.sleep(1)

    fname = os.path.join('tests','APDS9301_{}.txt'.format(id))
    with open(fname, 'w+') as f:
        for k, v in d.items():
            f.write("{},{}\n".format(k,v))


if __name__=="__main__":
    id = sys.argv[1]
    print("Sampling APDS9301 id: {}".format(id))
    main(id)
