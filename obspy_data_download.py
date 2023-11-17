#%% ----------IMPORT----------
import matplotlib.pyplot as plt
import copy
from obspy.clients.fdsn.client import Client
from obspy import UTCDateTime
from obspy.core.event import Catalog
from obspy.core.stream import Stream
from obspy import read_events
from obspy import read_inventory
import cartopy.crs as ccrs #good import?

#%% ----------GET_EVENTS----------
client=Client('INGV')

stime=UTCDateTime('2023-09-27T00:00:00')
etime=UTCDateTime('2023-10-03T00:00:00')
lat=40.8478     #pozzuoli
long=14.0918
rad_events=0.3  # ~30km

#events occurred in long period of time inside circular area (center pozzuoli)
print('getting events...')
cat=client.get_events(starttime=stime,endtime=etime,includearrivals=False,          
                      latitude=lat,longitude=long,maxradius=rad_events,
                      minmagnitude=2) 

#select only manually detected events
cat_manual=Catalog()
for ev in cat:
    if ev['origins'][0].evaluation_mode == 'manual':
        eid=ev.resource_id.id.split('=')[1]                                 # select id number
        cat_manual += client.get_events(includearrivals=True,eventid=eid)   #add to cat_manual the event

#eliminate automatic picking
for ev in cat_manual:
    ind_picks=[]
    for ind,pick in enumerate(ev.picks):
        if pick.evaluation_mode == 'automatic':
            ind_picks.append(ind)   
    for ind in reversed(ind_picks):
        del ev.picks[ind]

#save catologue
cat_manual.write('flegrei/cat_flegrei.xml',format='QUAKEML')

#%% ----------PLOT EVENTS----------

#cat_manual.plot() 

#%% ----------GET_STATIONS----------

#read event from local
catf=read_events('flegrei/cat_flegrei.xml')

rad_stations=0.1 # ~ 10km

#stations active for long period of time inside a circular area (center pozzuoli)
print('getting stations...')
inv=client.get_stations(starttime=stime,endtime=etime,
                        latitude=lat,longitude=long,maxradius=rad_stations,
                        level='response')                                   #instrumental response

#write inventory in local
inv.write('flegrei/inventory_f.xml',format='STATIONXML')                        #save

#read inventory from local
inv_f=read_inventory('flegrei/inventory_f.xml')

#%% ----------GET_WAVEFORMS----------

event_start=catf[0].origins[0].time
event_end=catf[0].origins[0].time +30


wave=Stream()
print('getting waveforms...')
# waveforms of event [0] recorded at all the stations in the inventory
# at origin time of the catalogue, only velocity components
for  station in inv_f.networks[0].stations:
    try:
        wave += client.get_waveforms(starttime=event_start,endtime=event_end,
                            network='IV',station=station.code,location='*', channel='EH?,HH?',
                            attach_response=True,) 
    except:
        print(station.code , 'station not found')

'''
#eliminate waveforms with sampling frequency==200
for tr in wave.traces:
    if tr.stats.sampling_rate == 200.:
        wave.remove(tr)
'''

#%% ----------SAVE & PLOTS----------

#write waveforms
wave.write('flegrei/wave_f.mseed',format='MSEED')

print('plotting waveforms')
wave.plot();

#%% -----------REMOVE INSTRUMENTAL RESPONSE-----------

wave_response=copy.deepcopy(wave)
wave_response.remove_response(output="VEL")
print('plotting waveforms without instrument response')
wave_response.plot();

plt.show()