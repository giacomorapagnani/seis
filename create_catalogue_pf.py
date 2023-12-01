from __future__ import print_function
import shutil
import glob
from pyrocko import util, model
km = 1000.

data_path='/'
file_sta='loc.txt'

def read_loki_catalog(fn):
    names = set()
    events = []
    with open(fn, 'r') as f:
        for line in f:
            w = line.split()

            t = util.str_to_time(w[0], format='%Y-%m-%dT%H:%M:%S.OPTFRAC') #converti str in formato tempo
            lat = float(w[1])
            lon = float(w[2])
            depth = float(w[3])*km

            name = util.time_to_str(t, format='%Y_%m_%d_%H_%M_%S') #converti tempo in str

            if name in names:
                continue

            names.add(name)

            event = model.Event(
                time=t,
                lat=lat,
                lon=lon,
                depth=depth,
                name=name)

            event.old_name = w[0].strip()

            events.append(event)

    return events

events_loki = read_loki_catalog(data_path+file_sta)
model.dump_events(events_loki, data_path +'loc.pf') #save events as pyrocko catalog