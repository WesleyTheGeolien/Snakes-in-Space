#!/usr/bin/env python
# coding: utf-8

# # Selecting values from Tiff

# We start of by making the necessary imports

# In[1]:


import pandas as pd # General data handling library -> aimed more at data science / flat matrices (multi indexing gets confusing)
import pandas_profiling # Adds tools for dataset
import numpy # Array manipulation library

import xarray as xr # Newish multidimension labbeled data manipulation library -> good with netcdf files also has rasterio importer for geotiffs
import hvplot.xarray # Add interactive plotting to xarray


# ## Load Points / Coordinates
# So lets first import start by loading the data in.
# 
# Pandas has some handy tools for reading excel files natively.
# 
# <div class='alert alert-info'>
#     These points don't have to come from a file you can adapt the notebook to write them inline or even do it iteractively by clicking on the grid
# </div>

# In[2]:


points = pd.read_excel('points.xlsx')
points


# Lets take a look at our data

# In[5]:


points.profile_report()


# There are lots of no data values there must have been some problems with saving the file.
# 
# Lets clean that up

# In[4]:


points = points.dropna()
points


# ## Import the geotiffs
# 
# Apparently the default library for importing geotiffs is `rasterio`. `xarray` have built on top of this library to be able to import geotiffs directly. So this isn't the most "pure" way but as we use `xarray` a lot in different places I believe this is the _best_ way.

# In[6]:


# In this example I am reading a file with (time, x, y) as dimensions
xarr = xr.open_rasterio('SSSjfm_IPSL4X_ModPg_180x360.tif')
xarr


# This has loaded the file as a `xarray.DataArray` we can see it has 3 coordinates, `x`, `y` and `band` in our case there is only one band so we are just going to remove it

# In[22]:


# Slice one of the bands
#.      band, y, x -> see dimensions above
img = xarr[0, :, :] 
# Lets take a look at our image
img.hvplot.image()


# ### Selecting points
# We can select a point with `.sel` we use the `method='nearest'` to get the nearest value to a point if it doesn't exisit

# In[23]:


img.sel(x=0.1, y=0.1, method="nearest")


# ### Lets try and get all the points

# In[9]:


points


# In[27]:


values = []
for i in range(len(points)):
    value = img.sel(x=points.loc[i, 'POINT_X (long)'] ,y= points.loc[i, 'POINT_Y (lat)'], method='nearest')
    values.append(value)
values = numpy.array(values)
values


# ### Now lets do it in a one liner!!!

# In[28]:


values = img.sel(x=points['POINT_X (long)'], y=points['POINT_Y (lat)'], method="nearest").pipe(numpy.diag)
values


# ## Store the values in the dataframe
# 
# No we store the values inside the data frame

# In[30]:


points['SSSjfm_IPSL4X_ModPg_180x360.tif'] = values
points


# In[31]:


points.to_csv('test.csv')


# # Your Turn try doing this for `SSTjas_IPSL4X_ModPg_180x360.tif`

# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# # Advanced
# 
# Here we get access to the points dynamically

# In[32]:


from holoviews import streams
import holoviews as hv


# In[33]:


# Sets up if we tap or double tap on the screen
tap = streams.SingleTap(transient=True)
double_tap = streams.DoubleTap(rename={'x': 'x2', 'y': 'y2'}, transient=True)


# ## Records coordinates and if we simple or double clicked

# In[34]:


taps = []

def record_taps(x, y, x2, y2):
    if None not in [x,y]:
        taps.append((x, y, 1))
    elif None not in [x2, y2]:
        taps.append((x2, y2, 2))
    return hv.Points(taps, vdims='Taps')


# ## Plotting
# 
# Go ahead click on the map!!

# In[35]:


taps_dmap = hv.DynamicMap(record_taps, streams=[tap, double_tap])

img.hvplot.image() * taps_dmap.opts(color='Taps', cmap={1: 'red', 2: 'gray'}, size=10, tools=['hover'])


# ## Get the results

# In[36]:


taps


# In[37]:


# get all the coords (remove the 1 or 2)
numpy.array(taps)[:, :2]

