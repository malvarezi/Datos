
# coding: utf-8

# In[1]:

get_ipython().magic('pylab inline')
from requests import Session
import pandas as pd
from bs4 import BeautifulSoup


# In[2]:

#LOAD CORDOBA DATA

session = Session()

# HEAD requests ask for *just* the headers, which is all you need to grab the
# session cookie
session.head('http://clima.bccba.com.ar/')

response = session.post(
    url='http://clima.bccba.com.ar/xmlDatosEstaciones.php',
)

#print(response.text)

#LOAD ENTRE RIOS DATA

session = Session()

# HEAD requests ask for *just* the headers, which is all you need to grab the
# session cookie
session.head('http://www.centrales.bolsacer.org.ar/inicio/')

response2 = session.post(
    url='http://www.centrales.bolsacer.org.ar/inicio/xmlDatosEstaciones.php',
)

#print(response2.text)


# In[3]:

soup = BeautifulSoup(response.text)
soup2 = BeautifulSoup(response2.text)


# In[4]:

data={}

for es in soup.find_all('estacion'): 
    vehicle = {child.name: child.text for child in es.findChildren()}
    for v in vehicle.keys():
#        data[v].append(vehicle[v])
        data.setdefault(v,[]).append(vehicle[v])
    
data2={}

for es in soup2.find_all('estacion'): 
    vehicle = {child.name: child.text for child in es.findChildren()}
    for v in vehicle.keys():
#        data[v].append(vehicle[v])
        data2.setdefault(v,[]).append(vehicle[v])


# In[5]:

wxframe=pd.DataFrame.from_dict(data, orient='columns', dtype=None)
wxframe2=pd.DataFrame.from_dict(data, orient='columns', dtype=None)

def fix_data(wxframe):
    wxframe['direccionviento'][wxframe['direccionviento'] == 'NORTE'] = '0'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'NOR NORESTE'] = '22.5'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'NORESTE'] = '45'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'ESTE NORESTE'] = '67.5'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'ESTE'] = '90'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'ESTE SUDESTE'] = '112.5'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'SUDESTE'] = '135'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'SUDESTE SUR'] = '157.5'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'SUR'] = '180'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'SUDOESTE SUR'] = '202.5'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'SUDOESTE'] = '225'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'OESTE SUDOESTE'] = '247.5'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'OESTE'] = '270'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'OESTE NOROESTE'] = '292.5'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'NOROESTE'] = '315'
    wxframe['direccionviento'][wxframe['direccionviento'] == 'NOR NOROESTE'] = '337.5'
    wxframe['temperatura'][wxframe['temperatura'] == '--']=''
    wxframe['direccionviento'][wxframe['direccionviento'] == '--']=np.nan
    wxframe['velocidadviento'][wxframe['velocidadviento'] == '--']=np.nan

    wxframe['u'] = wxframe['velocidadviento'].astype('float32') * np.sin(np.radians(wxframe['direccionviento'].astype('float32'))) * -1
    wxframe['v'] = wxframe['velocidadviento'].astype('float32') * np.cos(np.radians(wxframe['direccionviento'].astype('float32'))) * -1

    wxframe['fechamuestra']=pd.to_datetime(wxframe['fechamuestra'],format='%d/%m/%Y %H:%M').dt.tz_localize('America/Argentina/Buenos_Aires').dt.tz_convert('UTC')
    
    return wxframe


# In[6]:

wxframe=fix_data(wxframe)
wxframe=fix_data(wxframe2)


# In[7]:

get_ipython().magic('pylab inline')
from mpl_toolkits.basemap import Basemap

font = {'family': 'monospace',
        'weight': 'normal',
        'size': 10,
        }

plt.figure(figsize=(16,16))
m = Basemap(projection='merc',llcrnrlat=-35,urcrnrlat=-29.,llcrnrlon=-66,urcrnrlon=-61.,resolution='h')
m.etopo()
m.drawcoastlines()
m.drawstates()
m.drawcountries()

# draw parallels.
parallels = np.arange(-50.,-20.,1.)
m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10)
# draw meridians
meridians = np.arange(180.,360.,1.)
m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10)
x, y = m(np.float32(wxframe['longitud'].values),np.float32(wxframe['latitud'].values))
time=pd.to_datetime(str(np.max(wxframe['fechamuestra'].values)))
plt.title('Bolsa de Cereales de Córdoba Red de Estaciones Meteorológicas\n{} UTC'.format(time))

for i in np.arange(len(x)):
    plt.text(x[i],y[i],'{}'.format(wxframe['temperatura'][i]),
            verticalalignment='bottom', horizontalalignment='right',color='red', fontdict=font)
    plt.text(x[i],y[i],'{}'.format(wxframe['puntorocio'][i]),
            verticalalignment='top', horizontalalignment='right',color='green', fontdict=font)
    plt.text(x[i],y[i],'{}'.format(wxframe['precipitaciondia'][i]),
        verticalalignment='bottom', horizontalalignment='left',color='blue', fontdict=font)

    plt.barbs(x,y,wxframe['u']*1.94,wxframe['v']*1.94,lw=0.25,flip_barb=True,antialiased=1)
plt.savefig('map_test.pdf')


# In[8]:

#SAVE THE DATA TO CSV
datestr=pd.to_datetime(str(np.max(wxframe['fechamuestra'].values))).strftime('%Y-%m-%dT%H:%M:%SZ')
wxframe.to_csv(datestr+'_cordoba.csv')


# In[9]:

#READ BACK
datatest=pd.read_csv(datestr+'_cordoba.csv')
datatest


# In[ ]:



