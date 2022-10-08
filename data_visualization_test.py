import matplotlib as mpl
from matplotlib import artist
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import glob
import re


p = re.compile('x_z_con(\d+)')

# use glob to get all file
# path = os.getcwd() + "\\x_z_con"
path =r"C:\Users\robby\OneDrive - Athabasca University Students\Documents\COMP696\Data\x_z_con"

csv_files = glob.glob(os.path.join(path, "*.*"))

df_list = []

con_max = 0
con_min = 0

# loop over the list of csv files
for f in csv_files:
      
    m = p.search(f)
    if m:
        con = m.group(1)

        # read the csv file
        df = pd.read_csv(f,sep=' ',names=['x','z','concentration'])

        # update concentration max and min value
        t_min = df['concentration'].min()
        t_max = df['concentration'].max()

        if con_min == 0 or t_min < con_min:
            con_min = t_min

        if con_max == 0 or t_max > con_max:
            con_max = t_max

        df_list.append({'key':con, 'data':df})


df = df_list[0]['data']

fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot()


cmap = mpl.cm.cool
norm = mpl.colors.Normalize(vmin=con_min, vmax=con_max)
mappable = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)

# mappable.set_array(df['concentration'])
# color_values = mappable.get_array()

artist = ax.scatter(df['x'], df['z'], c=df['concentration'], s=100, cmap =cmap, vmin=con_min, vmax=con_max, animated=True)
# artist = ax.contourf(df['x'], df['z'], c=df['concentration'], s=100, cmap =cmap, vmin=con_min, vmax=con_max, animated=True)

title = ax.set_title("Data Change Observation", fontsize=20,animated=True)
fig.colorbar(mappable, ax=ax)

ax.set_xlabel('data x',fontsize=14)
ax.set_ylabel('data z',fontsize=14)
plt.show(block=False)
plt.pause(0.1)

bg = fig.canvas.copy_from_bbox(fig.bbox)
ax.draw_artist(artist)
fig.canvas.blit(fig.bbox)

# norm = mpl.colors.Normalize(vmin=con_min,vmax=con_max)
# plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax)

sample_index = 1

for item in df_list:
    df = item['data']
    fig.canvas.restore_region(bg)
    # mappable.set_array(df['concentration'])
    # color_values = mappable.get_array()

    # update the data 
    artist.set_array(df['concentration'])

    # update the title to show the sample #
    title.set_text("Data Change Observation - Sample: {}".format(sample_index))

    # redraw the artists
    ax.draw_artist(artist)
    ax.draw_artist(title)
    
    
    fig.canvas.blit(fig.bbox)
    fig.canvas.flush_events()
    
    
    plt.pause(0.5)

    # increase the sample counter
    sample_index = sample_index + 1


