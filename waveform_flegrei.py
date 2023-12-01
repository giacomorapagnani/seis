# %%import
import matplotlib.pyplot as plt

from obspy.clients.fdsn.client import Client
from obspy import UTCDateTime
from obspy.core.event import Catalog
from obspy.core.stream import Stream
from obspy.core.event import Event
from obspy.core.event import Origin
from obspy.core.event import Magnitude
from obspy import read_events
from obspy import read_inventory
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import pickle


# %% read catalogues
catINGV=read_events('flegrei_2014_2023_INGV/catalogue_flegrei.xml')

catOV=read_events('flegrei_2014_2023_GOSSIP/catalogue_flegrei.xml')

client=Client('INGV')

# %% GET Stations
'''
stime=UTCDateTime('2014-01-01T00:00:00')
etime=UTCDateTime('2023-11-20T00:00:00')

lat=40.8478
long=14.0918
rad_events=0.5
inv=client.get_stations(starttime=stime,endtime=etime,
                        latitude=lat,longitude=long,maxradius=rad_events,
                        level='response')                                   #instrumental response
inv
'''
# plot station location
#inv.plot(projection='local',resolution='h');

# save
#inv.write('flegrei_2014_2023_INGV/inventory_flegrei.xml',format='STATIONXML')

#plot instrument response of a station
#inv.plot_response(min_freq=1E-4,station='SORR',channel='[EH]H?');

# %% GET Waveform 

#read inventory
inv_f=read_inventory('flegrei_2014_2023_INGV/inventory_flegrei.xml')

catOV_mag = catOV.filter("magnitude >= 3.0")
for ev in catOV_mag:
    origin_time=ev.origins[0].time
    evID=ev.resource_id.id.split('/')[1]
    print('event id: ',evID)
    print('origin time event:',origin_time)
    print('extimated magnitude:',ev.magnitudes[0].mag)


    event_start=origin_time -10
    event_end=origin_time +50

    wave=Stream()
    for network in inv_f:
        for  station in network.stations:
            try:
                wave += client.get_waveforms(starttime=event_start,endtime=event_end,
                                    network=network.code,station=station.code,location='*', channel='HH?',
                                    attach_response=True,)
            except:
                #print(station.code , 'station not found')
                continue

    print('traces found:',len(wave.traces))

    wave.merge(fill_value=0)
    # trim over the [t1, t2] interval
    wave.trim(starttime=event_start, endtime=event_end, pad=True, fill_value=0)

    '''
    # remove trend
    wave.detrend("demean")
    
    #remove instrumental response
    pre_filt = [0.01, 0.1, 25,30]
    
    #remove instrumental response
    wave.remove_response(inventory=inv_f, output='DISP', pre_filt=pre_filt) #output=VEL ??
    '''

    wave.write('waveform/wave_'+ evID +'.mseed',format='MSEED')
    print('saved!')


