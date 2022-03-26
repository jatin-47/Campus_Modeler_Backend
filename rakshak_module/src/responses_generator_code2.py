
#!/usr/bin/env python
# coding: utf-8

# ## IMPORTS

# In[157]:


import numpy as np
import pandas as pd
import copy
import random
import math


# ## READ DATA

# In[158]:


data=pd.read_csv('rakshak/data_IITJ/survey_data/Faculty and Staff choices.csv');


# In[159]:


data


# ## CREATE ALL POSSIBLE LISTS

# In[160]:


types=[];
for i in range(data['Timestamp'].size):
    val=data['Select your role'][i];
    types.append(val);
types=list(set(types));
types

eateries=[];
for i in range(data['Timestamp'].size):
    vals=data['What are the eateries that you frequently visit?'][i].split(', ');
    for val in vals:
        eateries.append(val);
eateries = list(set(eateries));

buildings=[];
for i in range(data['Timestamp'].size):
    vals=data['What are your frequent places of visit outside of working hours?'][i].split(', ');
    for val in vals:
        buildings.append(val);
buildings=list(set(buildings));

times=[];
for i in range(data['Timestamp'].size):
    vals1=data['Select all your typical working hours on weekdays?'][i].split(', ');
    vals2=data['Select all your typical working hours on weekends?'][i].split(', ');
    for val in vals1:
        times.append(val);
    for val in vals2:
        times.append(val);
times=list(set(times));


# ## GENERATE PROBABILITIES

# In[161]:


template=dict.fromkeys(types,0);
T_template={i:dict.fromkeys(times,1) for i in types};
gen1=copy.deepcopy(template);
gen1_count=copy.deepcopy(template);
gen1_weights=copy.deepcopy(T_template);


# In[162]:


for i in range(data['Timestamp'].size):
    vals=data['Select all your typical working hours on weekdays?'][i].split(', ');
    #num
    TYPE=data['Select your role'][i]
    gen1[TYPE] = gen1[TYPE] + len(vals);
    gen1_count[TYPE] = gen1_count[TYPE]+1;
    #weights
    for val in vals:
        gen1_weights[TYPE][val] = gen1_weights[TYPE][val]+1;


# In[163]:


gen2=copy.deepcopy(template);
gen2_count=copy.deepcopy(template);
gen2_weights=copy.deepcopy(T_template);


# In[164]:


for i in range(data['Timestamp'].size):
    vals=data['Select all your typical working hours on weekends?'][i].split(', ');
    #num
    TYPE=data['Select your role'][i]
    gen2[TYPE] = gen2[TYPE] + len(vals);
    gen2_count[TYPE] = gen2_count[TYPE]+1;
    #weights
    for val in vals:
        gen2_weights[TYPE][val] = gen2_weights[TYPE][val]+1;


# In[165]:


L_template={i:dict.fromkeys(buildings,1) for i in types}
gen3=copy.deepcopy(template);
gen3_count=copy.deepcopy(template);
gen3_weights=copy.deepcopy(L_template);


# In[166]:


for i in range(data['Timestamp'].size):
    vals=data['What are your frequent places of visit outside of working hours?'][i].split(', ');
    #num
    TYPE=data['Select your role'][i];
    gen3[TYPE] = gen3[TYPE] + len(vals);
    gen3_count[TYPE] = gen3_count[TYPE]+1;
    for val in vals:
        gen3_weights[TYPE][val] = gen3_weights[TYPE][val]+1;


# In[167]:


gen4=copy.deepcopy(template);
gen4_count=copy.deepcopy(template);


# In[168]:


for i in range(data['Timestamp'].size):
    val=data['How many times do you usually eat out (Canteen/Restaurants/Eateries) in a week? [-]'][i];
    TYPE=data['Select your role'][i]
    gen4[TYPE] = gen4[TYPE] + val;
    gen4_count[TYPE] = gen4_count[TYPE]+1;


# In[169]:


E_template={i:dict.fromkeys(eateries,1) for i in types}
gen5=copy.deepcopy(template);
gen5_count=copy.deepcopy(template);
gen5_weights=copy.deepcopy(E_template)


# In[170]:


for i in range(data['Timestamp'].size):
    vals=data['What are the eateries that you frequently visit?'][i].split(', ');
    #num
    TYPE=data['Select your role'][i]
    gen5[TYPE] = gen5[TYPE] + len(vals);
    gen5_count[TYPE] = gen5_count[TYPE]+1;
    for val in vals:
        gen5_weights[TYPE][val] = gen5_weights[TYPE][val]+1;


# ## NORMALIZE WEIGHTS AND COUNTS

# In[171]:


for i in gen1:
    if gen1_count[i]!=0:
        gen1[i]/=gen1_count[i];

for i in gen2:
    if gen2_count[i]!=0:
        gen2[i]/=gen2_count[i];

for i in gen3:
    if gen3_count[i]!=0:
        gen3[i]/=gen3_count[i];

for i in gen4:
    if gen4_count[i]!=0:
        gen4[i]/=gen4_count[i];


# In[172]:


for i in gen1_weights:
    count=0;
    for j in gen1_weights[i]:
        count+=gen1_weights[i][j];
    for j in gen1_weights[i]:
        if count!=0:
            gen1_weights[i][j]/=count;

for i in gen2_weights:
    count=0;
    for j in gen2_weights[i]:
        count+=gen2_weights[i][j];
    for j in gen2_weights[i]:
        if count!=0:
            gen2_weights[i][j]/=count;

for i in gen3_weights:
    count=0;
    for j in gen3_weights[i]:
        count+=gen3_weights[i][j];
    for j in gen3_weights[i]:
        if count!=0:
            gen3_weights[i][j]/=count;

for i in gen5_weights:
    count=0;
    for j in gen5_weights[i]:
        count+=gen5_weights[i][j];
    for j in gen5_weights[i]:
        if count!=0:
            gen5_weights[i][j]/=count;


# ## VARIANCE CALCULATION

# In[173]:


g1_mean=0;
g1_var=0;
for i in range(data['Timestamp'].size):
    vals=data['Select all your typical working hours on weekdays?'][i].split(', ');
    g1_mean+=len(vals);
g1_mean/=(data['Timestamp'].size);
for i in range(data['Timestamp'].size):
    vals=data['Select all your typical working hours on weekdays?'][i].split(', ');
    g1_var+=(len(vals)-g1_mean)**2;
g1_var/=(data['Timestamp'].size);
g1_var=math.sqrt(g1_var);


# In[174]:


g2_mean=0;
g2_var=0;
for i in range(data['Timestamp'].size):
    vals=data['Select all your typical working hours on weekends?'][i].split(', ');
    g2_mean+=len(vals);
g2_mean/=(data['Timestamp'].size);
for i in range(data['Timestamp'].size):
    vals=data['Select all your typical working hours on weekends?'][i].split(', ');
    g2_var+=(len(vals)-g2_mean)**2;
g2_var/=(data['Timestamp'].size);
g2_var=math.sqrt(g2_var);


# In[175]:


g3_mean=0;
g3_var=0;
for i in range(data['Timestamp'].size):
    vals=data['What are your frequent places of visit outside of working hours?'][i].split(', ');
    g3_mean+=len(vals);
g3_mean/=(data['Timestamp'].size);
for i in range(data['Timestamp'].size):
    vals=data['What are your frequent places of visit outside of working hours?'][i].split(', ');
    g3_var+=(len(vals)-g3_mean)**2;
g3_var/=(data['Timestamp'].size);
g3_var=math.sqrt(g3_var);


# In[176]:


g4_mean=0;
g4_var=0;
for i in range(data['Timestamp'].size):
    val=data['How many times do you usually eat out (Canteen/Restaurants/Eateries) in a week? [-]'][i];
    g4_mean+=val;
g4_mean/=(data['Timestamp'].size);
for i in range(data['Timestamp'].size):
    val=data['How many times do you usually eat out (Canteen/Restaurants/Eateries) in a week? [-]'][i];
    g4_var+=(val-g4_mean)**2;
g4_var/=(data['Timestamp'].size);
g4_var=math.sqrt(g4_var);


# ## GENERATING RECORD

# In[177]:


def generate_record2(person_type):
    record=[[],[],[],0,0];
    #1
    cnt=gen1[person_type];
    cnt=round(np.random.normal(cnt,g1_var))
    cnt=min(max(1,cnt),len(times)-1);
    req=copy.deepcopy(gen1_weights[person_type]);
    if cnt!=1:
        req['None']=0;
    record[0]=[cnt,req];
    #2
    cnt=gen2[person_type];
    cnt=round(np.random.normal(cnt,g2_var))
    cnt=min(max(1,cnt),len(times)-1);
    req=copy.deepcopy(gen2_weights[person_type]);
    if cnt!=1:
        req['None']=0;
    record[1]=[cnt,req];
    #3
    cnt=gen3[person_type];
    cnt=round(np.random.normal(cnt,g3_var))
    cnt=min(max(1,cnt),len(buildings)-1);
    req=copy.deepcopy(gen3_weights[person_type]);
    if cnt!=1:
        req['None']=0;
    record[2]=[cnt,req];
    #4
    cnt=gen4[person_type];
    cnt=round(np.random.normal(cnt,g4_var))
    cnt=min(max(1,cnt),len(eateries)-1);
    record[3]=cnt;
    #5
    req=copy.deepcopy(gen5_weights[person_type]);
    record[4]=req;
    if record[3]!=1:
        record[4]['None']=0;
    return record;


# In[182]:


# print(generate_record2('Staff'))


# In[132]:


# buildings


# In[ ]:




