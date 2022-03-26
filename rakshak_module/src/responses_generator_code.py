#!/usr/bin/env python
# coding: utf-8

# In[409]:


import numpy as np
import pandas as pd
import copy
import random
import math


# ## read data_IITKGP

# In[410]:


data=pd.read_csv('rakshak/data_IITJ/survey_data/Student Choices.csv');
df=pd.read_csv('rakshak/data_IITJ/survey_data/building_name_to_id_mapping.csv');


# In[411]:


data


# In[412]:


df['ID'] = df['ID'].astype(int)
t_mapping = df["ID"]
t_mapping.index = df["Building"]
t_mapping = t_mapping.to_dict()


# In[413]:


mapping={};
for key in t_mapping:
    if(isinstance(key, str)):
        mapping[key.upper()]=t_mapping[key];
    else:
        mapping[key]=t_mapping[key];


# In[414]:


deps=[];
for i in range(data['Timestamp'].size):
    val=data['Your department (Use short code ex. CSE, ME, EE, BB)'][i];
    deps.append(val);
deps=list(set(deps))

buildings=[];
for i in range(data['Timestamp'].size):
    vals1=data['During 𝘄𝗲𝗲𝗸𝗱𝗮𝘆𝘀, what are your frequent places of visit?'][i].split(', ');
    vals2=data['During 𝘄𝗲𝗲𝗸𝗲𝗻𝗱𝘀, what are your frequent places of visit?'][i].split(', ');
    for val in vals1:
        buildings.append(val);
    for val in vals2:
        buildings.append(val);
buildings=list(set(buildings));

eateries=[];
for i in range(data['Timestamp'].size):
    vals=data['What are the eateries that you frequently visit?'][i].split(', ');
    for val in vals:
        eateries.append(val);
eateries = list(set(eateries));

sleep_times=[];
for i in range(data['Timestamp'].size):
    vals=data['When do you usually return to your room to sleep (if you go out)?'][i].split(', ');
    for val in vals:
        sleep_times.append(val);
sleep_times = list(set(sleep_times));

times=[];
for i in range(data['Timestamp'].size):
    vals=data['Choose the time frames when you usually step out from your hostel during 𝘄𝗲𝗲𝗸𝗲𝗻𝗱𝘀.'][i].split(', ');
    for val in vals:
        times.append(val);
times = list(set(times));

years=[];
for i in range(data['Timestamp'].size):
    vals=data['Current Year of study'][i].split(', ');
    for val in vals:
        years.append(val);
years = list(set(years));

courses=[];
for i in range(data['Timestamp'].size):
    vals=data['Your academic program'][i].split(', ');
    for val in vals:
        courses.append(val);
courses = list(set(courses));


# In[415]:


hostels=[i for i in range(42,54)]; hostels.append(-1);
courses=['UG','PG'];


# ## weights

# In[416]:


weights={'department':0.25, 'year':0.25, 'hostel':0.25, 'course':0.25};


# ## generate individual distributions

# In[417]:


template={'department':dict.fromkeys(deps,0), 'year':dict.fromkeys(years,0), 
          'hostel':dict.fromkeys(hostels,0), 'course':dict.fromkeys(courses,0)};
gen1=copy.deepcopy(template)
gen1_count=copy.deepcopy(template)


# In[418]:


for i in range(data['Timestamp'].size):
    val=data['When you move outside your hostel, with how many people do you usually move together? [-]'][i];
    #DEP
    DEP=data['Your department (Use short code ex. CSE, ME, EE, BB)'][i].upper();
    gen1['department'][DEP] = gen1['department'][DEP] + val;
    gen1_count['department'][DEP] = gen1_count['department'][DEP]+1;
    #hostel
    if(isinstance(data['Hostel of Residence'][i], str)):
        HOS=mapping[data['Hostel of Residence'][i].strip().upper()];
        gen1['hostel'][HOS] = gen1['hostel'][HOS]+val;
        gen1_count['hostel'][HOS] = gen1_count['hostel'][HOS]+1;
    #course
    COURSE=data['Your academic program'][i];
    gen1['course'][COURSE] = gen1['course'][COURSE] + val;
    gen1_count['course'][COURSE] = gen1_count['course'][COURSE] + 1;
    #year
    YEAR=data['Current Year of study'][i];
    gen1['year'][YEAR] = gen1['year'][YEAR] + val;
    gen1_count['year'][YEAR] = gen1_count['year'][YEAR] + 1;


# In[419]:


gen2=copy.deepcopy(template);
gen2_count=copy.deepcopy(template);


# In[420]:


for i in range(data['Timestamp'].size):
    val=data['How many different friend circles do you have? [-]'][i];
    #DEP
    DEP=data['Your department (Use short code ex. CSE, ME, EE, BB)'][i].upper();
    gen2['department'][DEP] = gen2['department'][DEP] + val;
    gen2_count['department'][DEP] = gen2_count['department'][DEP]+1;
    #hostel
    if(isinstance(data['Hostel of Residence'][i], str)):
        HOS=mapping[data['Hostel of Residence'][i].strip().upper()];
        gen2['hostel'][HOS] = gen2['hostel'][HOS]+val;
        gen2_count['hostel'][HOS] = gen2_count['hostel'][HOS]+1;
    #course
    COURSE=data['Your academic program'][i];
    gen2['course'][COURSE] = gen2['course'][COURSE] + val;
    gen2_count['course'][COURSE] = gen2_count['course'][COURSE] + 1;
    #year
    YEAR=data['Current Year of study'][i];
    gen2['year'][YEAR] = gen2['year'][YEAR] + val;
    gen2_count['year'][YEAR] = gen2_count['year'][YEAR] + 1;


# In[421]:


gen3=copy.deepcopy(template);
gen3_count=copy.deepcopy(template);


# In[422]:


for i in range(data['Timestamp'].size):
    val=data['During weekdays, apart from class hours, 𝗵𝗼𝘄 𝗺𝗮𝗻𝘆 𝗱𝗮𝘆𝘀 𝗶𝗻 𝗮 𝘄𝗲𝗲𝗸 do you usually step out from your hostel?  [-]'][i];
    #DEP
    DEP=data['Your department (Use short code ex. CSE, ME, EE, BB)'][i].upper();
    gen3['department'][DEP] = gen3['department'][DEP] + val;
    gen3_count['department'][DEP] = gen3_count['department'][DEP]+1;
    #hostel
    if(isinstance(data['Hostel of Residence'][i], str)):
        HOS=mapping[data['Hostel of Residence'][i].strip().upper()];
        gen3['hostel'][HOS] = gen3['hostel'][HOS]+val;
        gen3_count['hostel'][HOS] = gen3_count['hostel'][HOS]+1;
    #course
    COURSE=data['Your academic program'][i];
    gen3['course'][COURSE] = gen3['course'][COURSE] + val;
    gen3_count['course'][COURSE] = gen3_count['course'][COURSE] + 1;
    #year
    YEAR=data['Current Year of study'][i];
    gen3['year'][YEAR] = gen3['year'][YEAR] + val;
    gen3_count['year'][YEAR] = gen3_count['year'][YEAR] + 1;


# In[423]:


gen4=copy.deepcopy(template);
gen4_count=copy.deepcopy(template);


# In[424]:


for i in range(data['Timestamp'].size):
    val=data['During weekdays, apart from class hours, roughly for 𝗵𝗼𝘄 𝗺𝗮𝗻𝘆 𝗵𝗼𝘂𝗿𝘀 do you stay outside your hostel 𝗶𝗻 𝗮 𝗱𝗮𝘆?  [-]'][i];
    #DEP
    DEP=data['Your department (Use short code ex. CSE, ME, EE, BB)'][i].upper();
    gen4['department'][DEP] = gen4['department'][DEP] + val;
    gen4_count['department'][DEP] = gen4_count['department'][DEP]+1;
    #hostel
    if(isinstance(data['Hostel of Residence'][i], str)):
        HOS=mapping[data['Hostel of Residence'][i].strip().upper()];
        gen4['hostel'][HOS] = gen4['hostel'][HOS]+val;
        gen4_count['hostel'][HOS] = gen4_count['hostel'][HOS]+1;
    #course
    COURSE=data['Your academic program'][i];
    gen4['course'][COURSE] = gen4['course'][COURSE] + val;
    gen4_count['course'][COURSE] = gen4_count['course'][COURSE] + 1;
    #year
    YEAR=data['Current Year of study'][i];
    gen4['year'][YEAR] = gen4['year'][YEAR] + val;
    gen4_count['year'][YEAR] = gen4_count['year'][YEAR] + 1;


# In[425]:


L_template={'department':{i:dict.fromkeys(buildings,1) for i in deps}, 'year':{i:dict.fromkeys(buildings,1) for i in years},
           'course':{i:dict.fromkeys(buildings,1) for i in courses}, 'hostel':{i:dict.fromkeys(buildings,1) for i in hostels}};
gen5=copy.deepcopy(template);
gen5_count=copy.deepcopy(template);
gen5_weights=copy.deepcopy(L_template)


# In[426]:


for i in range(data['Timestamp'].size):
    vals=data['During 𝘄𝗲𝗲𝗸𝗱𝗮𝘆𝘀, what are your frequent places of visit?'][i].split(', ');
    #DEP
    DEP=data['Your department (Use short code ex. CSE, ME, EE, BB)'][i].upper();
    gen5['department'][DEP] = gen5['department'][DEP] + len(vals);
    gen5_count['department'][DEP] = gen5_count['department'][DEP]+1;
    #hostel
    if(isinstance(data['Hostel of Residence'][i], str)):
        HOS=mapping[data['Hostel of Residence'][i].strip().upper()];
        gen5['hostel'][HOS] = gen5['hostel'][HOS]+len(vals);
        gen5_count['hostel'][HOS] = gen5_count['hostel'][HOS]+1;
    #course
    COURSE=data['Your academic program'][i];
    gen5['course'][COURSE] = gen5['course'][COURSE] + len(vals);
    gen5_count['course'][COURSE] = gen5_count['course'][COURSE] + 1;
    #year
    YEAR=data['Current Year of study'][i];
    gen5['year'][YEAR] = gen5['year'][YEAR] + len(vals);
    gen5_count['year'][YEAR] = gen5_count['year'][YEAR] + 1;
    for val in vals:
        gen5_weights['department'][DEP][val] = gen5_weights['department'][DEP][val]+1;
        gen5_weights['hostel'][HOS][val] = gen5_weights['hostel'][HOS][val]+1;
        gen5_weights['course'][COURSE][val] = gen5_weights['course'][COURSE][val]+1;
        gen5_weights['year'][YEAR][val] = gen5_weights['year'][YEAR][val]+1;


# In[427]:


gen6=copy.deepcopy(template);
gen6_count=copy.deepcopy(template);


# In[428]:


for i in range(data['Timestamp'].size):
    val=data['During weekdays, apart from class hours, how many 𝗱𝗶𝗳𝗳𝗲𝗿𝗲𝗻𝘁 𝗽𝗹𝗮𝗰𝗲𝘀 (from the above list) do you usually visit in a 𝘀𝗶𝗻𝗴𝗹𝗲 𝗱𝗮𝘆? [-]'][i];
    #DEP
    DEP=data['Your department (Use short code ex. CSE, ME, EE, BB)'][i].upper();
    gen6['department'][DEP] = gen6['department'][DEP] + val;
    gen6_count['department'][DEP] = gen6_count['department'][DEP]+1;
    #hostel
    if(isinstance(data['Hostel of Residence'][i], str)):
        HOS=mapping[data['Hostel of Residence'][i].strip().upper()];
        gen6['hostel'][HOS] = gen6['hostel'][HOS]+val;
        gen6_count['hostel'][HOS] = gen6_count['hostel'][HOS]+1;
    #course
    COURSE=data['Your academic program'][i];
    gen6['course'][COURSE] = gen6['course'][COURSE] + val;
    gen6_count['course'][COURSE] = gen6_count['course'][COURSE] + 1;
    #year
    YEAR=data['Current Year of study'][i];
    gen6['year'][YEAR] = gen6['year'][YEAR] + val;
    gen6_count['year'][YEAR] = gen6_count['year'][YEAR] + 1;


# In[429]:


gen7=copy.deepcopy(template);
gen7_count=copy.deepcopy(template);


# In[430]:


for i in range(data['Timestamp'].size):
    val=data['How many times do you usually eat out (Canteen/Restaurants/Eateries) 𝗶𝗻 𝗮 𝘄𝗲𝗲𝗸? [-]'][i];
    #DEP
    DEP=data['Your department (Use short code ex. CSE, ME, EE, BB)'][i].upper();
    gen7['department'][DEP] = gen7['department'][DEP] + val;
    gen7_count['department'][DEP] = gen7_count['department'][DEP]+1;
    #hostel
    if(isinstance(data['Hostel of Residence'][i], str)):
        HOS=mapping[data['Hostel of Residence'][i].strip().upper()];
        gen7['hostel'][HOS] = gen7['hostel'][HOS]+val;
        gen7_count['hostel'][HOS] = gen7_count['hostel'][HOS]+1;
    #course
    COURSE=data['Your academic program'][i];
    gen7['course'][COURSE] = gen7['course'][COURSE] + val;
    gen7_count['course'][COURSE] = gen7_count['course'][COURSE] + 1;
    #year
    YEAR=data['Current Year of study'][i];
    gen7['year'][YEAR] = gen7['year'][YEAR] + val;
    gen7_count['year'][YEAR] = gen7_count['year'][YEAR] + 1;


# In[431]:


E_template={'department':{i:dict.fromkeys(eateries,1) for i in deps}, 'year':{i:dict.fromkeys(eateries,1) for i in years},
           'course':{i:dict.fromkeys(eateries,1) for i in courses}, 'hostel':{i:dict.fromkeys(eateries,1) for i in hostels}};
gen8=copy.deepcopy(template);
gen8_count=copy.deepcopy(template);
gen8_weights=copy.deepcopy(E_template)


# In[432]:


for i in range(data['Timestamp'].size):
    vals=data['What are the eateries that you frequently visit?'][i].split(', ');
    #DEP
    DEP=data['Your department (Use short code ex. CSE, ME, EE, BB)'][i].upper();
    gen8['department'][DEP] = gen8['department'][DEP] + len(vals);
    gen8_count['department'][DEP] = gen8_count['department'][DEP]+1;
    #hostel
    if(isinstance(data['Hostel of Residence'][i], str)):
        HOS=mapping[data['Hostel of Residence'][i].strip().upper()];
        gen8['hostel'][HOS] = gen8['hostel'][HOS]+len(vals);
        gen8_count['hostel'][HOS] = gen8_count['hostel'][HOS]+1;
    #course
    COURSE=data['Your academic program'][i];
    gen8['course'][COURSE] = gen8['course'][COURSE] + len(vals);
    gen8_count['course'][COURSE] = gen8_count['course'][COURSE] + 1;
    #year
    YEAR=data['Current Year of study'][i];
    gen8['year'][YEAR] = gen8['year'][YEAR] + len(vals);
    gen8_count['year'][YEAR] = gen8_count['year'][YEAR] + 1;
    for val in vals:
        gen8_weights['department'][DEP][val] = gen8_weights['department'][DEP][val]+1;
        gen8_weights['hostel'][HOS][val] = gen8_weights['hostel'][HOS][val]+1;
        gen8_weights['course'][COURSE][val] = gen8_weights['course'][COURSE][val]+1;
        gen8_weights['year'][YEAR][val] = gen8_weights['year'][YEAR][val]+1;


# #### G9 to be filled here

# In[433]:


T_template={'department':{i:dict.fromkeys(times,1) for i in deps}, 'year':{i:dict.fromkeys(times,1) for i in years},
           'course':{i:dict.fromkeys(times,1) for i in courses}, 'hostel':{i:dict.fromkeys(times,1) for i in hostels}};
gen9=copy.deepcopy(template);
gen9_count=copy.deepcopy(template);
gen9_weights=copy.deepcopy(T_template);


# In[434]:


for i in range(data['Timestamp'].size):
    vals=data['Choose the time frames when you usually step out from your hostel during 𝘄𝗲𝗲𝗸𝗲𝗻𝗱𝘀.'][i].split(', ');
    #DEP
    DEP=data['Your department (Use short code ex. CSE, ME, EE, BB)'][i].upper();
    gen9['department'][DEP] = gen9['department'][DEP] + len(vals);
    gen9_count['department'][DEP] = gen9_count['department'][DEP]+1;
    #hostel
    if(isinstance(data['Hostel of Residence'][i], str)):
        HOS=mapping[data['Hostel of Residence'][i].strip().upper()];
        gen9['hostel'][HOS] = gen9['hostel'][HOS]+len(vals);
        gen9_count['hostel'][HOS] = gen9_count['hostel'][HOS]+1;
    #course
    COURSE=data['Your academic program'][i];
    gen9['course'][COURSE] = gen9['course'][COURSE] + len(vals);
    gen9_count['course'][COURSE] = gen9_count['course'][COURSE] + 1;
    #year
    YEAR=data['Current Year of study'][i];
    gen9['year'][YEAR] = gen9['year'][YEAR] + len(vals);
    gen9_count['year'][YEAR] = gen9_count['year'][YEAR] + 1;
    for val in vals:
        gen9_weights['department'][DEP][val] = gen9_weights['department'][DEP][val]+1;
        gen9_weights['hostel'][HOS][val] = gen9_weights['hostel'][HOS][val]+1;
        gen9_weights['course'][COURSE][val] = gen9_weights['course'][COURSE][val]+1;
        gen9_weights['year'][YEAR][val] = gen9_weights['year'][YEAR][val]+1;


# In[435]:


gen10=copy.deepcopy(template);
gen10_count=copy.deepcopy(template); 
gen10_weights=copy.deepcopy(L_template);


# In[436]:


for i in range(data['Timestamp'].size):
    vals=data['During 𝘄𝗲𝗲𝗸𝗲𝗻𝗱𝘀, what are your frequent places of visit?'][i].split(', ');
    #DEP
    DEP=data['Your department (Use short code ex. CSE, ME, EE, BB)'][i].upper();
    gen10['department'][DEP] = gen10['department'][DEP] + len(vals);
    gen10_count['department'][DEP] = gen10_count['department'][DEP]+1;
    #hostel
    if(isinstance(data['Hostel of Residence'][i], str)):
        HOS=mapping[data['Hostel of Residence'][i].strip().upper()];
        gen10['hostel'][HOS] = gen10['hostel'][HOS]+len(vals);
        gen10_count['hostel'][HOS] = gen10_count['hostel'][HOS]+1;
    #course
    COURSE=data['Your academic program'][i];
    gen10['course'][COURSE] = gen10['course'][COURSE] + len(vals);
    gen10_count['course'][COURSE] = gen10_count['course'][COURSE] + 1;
    #year
    YEAR=data['Current Year of study'][i];
    gen10['year'][YEAR] = gen10['year'][YEAR] + len(vals);
    gen10_count['year'][YEAR] = gen10_count['year'][YEAR] + 1;
    for val in vals:
        gen10_weights['department'][DEP][val] = gen10_weights['department'][DEP][val]+1;
        gen10_weights['hostel'][HOS][val] = gen10_weights['hostel'][HOS][val]+1;
        gen10_weights['course'][COURSE][val] = gen10_weights['course'][COURSE][val]+1;
        gen10_weights['year'][YEAR][val] = gen10_weights['year'][YEAR][val]+1;


# In[437]:


S_template={'department':{i:dict.fromkeys(sleep_times,1) for i in deps}, 'year':{i:dict.fromkeys(sleep_times,1) for i in years},
           'course':{i:dict.fromkeys(sleep_times,1) for i in courses}, 'hostel':{i:dict.fromkeys(sleep_times,1) for i in hostels}}
gen11_weights=copy.deepcopy(S_template);


# In[438]:


for i in range(data['Timestamp'].size):
    vals=data['When do you usually return to your room to sleep (if you go out)?'][i].split(', ');
    #DEP
    DEP=data['Your department (Use short code ex. CSE, ME, EE, BB)'][i].upper();
    gen11_weights['department'][DEP][vals[0]] = gen11_weights['department'][DEP][vals[0]] + 1;
    #hostel
    if(isinstance(data['Hostel of Residence'][i], str)):
        HOS=mapping[data['Hostel of Residence'][i].strip().upper()];
        gen11_weights['hostel'][HOS][vals[0]] = gen11_weights['hostel'][HOS][vals[0]]+1;
    #course
    COURSE=data['Your academic program'][i];
    gen11_weights['course'][COURSE][vals[0]] = gen11_weights['course'][COURSE][vals[0]] + 1;
    #year
    YEAR=data['Current Year of study'][i];
    gen11_weights['year'][YEAR][vals[0]] = gen11_weights['year'][YEAR][vals[0]] + 1;


# ## normalize weights, and counts.

# In[439]:


for i in gen1:
    for j in gen1[i]: 
        if(gen1[i][j]!=0):
            gen1[i][j]/=gen1_count[i][j];
            
for i in gen2:
    for j in gen2[i]: 
        if(gen2[i][j]!=0):
            gen2[i][j]/=gen2_count[i][j];
            
for i in gen3:
    for j in gen3[i]: 
        if(gen3[i][j]!=0):
            gen3[i][j]/=gen3_count[i][j];
            
for i in gen4:
    for j in gen4[i]: 
        if(gen4[i][j]!=0):
            gen4[i][j]/=gen4_count[i][j];
            
for i in gen6:
    for j in gen6[i]: 
        if(gen6[i][j]!=0):
            gen6[i][j]/=gen6_count[i][j];
            
for i in gen7:
    for j in gen7[i]: 
        if(gen7[i][j]!=0):
            gen7[i][j]/=gen7_count[i][j];
            
for i in gen9:
    for j in gen9[i]: 
        if(gen9[i][j]!=0):
            gen9[i][j]/=gen9_count[i][j];

            


# In[440]:


for i in gen5_weights:
    for j in gen5_weights[i]:
        count=0;
        for k in gen5_weights[i][j]:
            count+=gen5_weights[i][j][k];
        for k in gen5_weights[i][j]:
            if(count!=0):
                gen5_weights[i][j][k]/=count;
                
for i in gen8_weights:
    for j in gen8_weights[i]:
        count=0;
        for k in gen8_weights[i][j]:
            count+=gen8_weights[i][j][k];
        for k in gen8_weights[i][j]:
            if(count!=0):
                gen8_weights[i][j][k]/=count;
                
for i in gen9_weights:
    for j in gen9_weights[i]:
        count=0;
        for k in gen9_weights[i][j]:
            count+=gen9_weights[i][j][k];
        for k in gen9_weights[i][j]:
            if(count!=0):
                gen9_weights[i][j][k]/=count;

for i in gen10_weights:
    for j in gen10_weights[i]:
        count=0;
        for k in gen10_weights[i][j]:
            count+=gen10_weights[i][j][k];
        for k in gen10_weights[i][j]:
            if(count!=0):
                gen10_weights[i][j][k]/=count;
                    
for i in gen11_weights:
    for j in gen11_weights[i]:
        count=0;
        for k in gen11_weights[i][j]:
            count+=gen11_weights[i][j][k];
        for k in gen11_weights[i][j]:
            if(count!=0):
                gen11_weights[i][j][k]/=count;


# ## Variance Calculation

# In[441]:


g1_mean=0;
g1_var=0;
for i in range(data['Timestamp'].size):
    val=data['When you move outside your hostel, with how many people do you usually move together? [-]'][i];
    g1_mean+=val;
g1_mean/=(data['Timestamp'].size);
for i in range(data['Timestamp'].size):
    val=data['When you move outside your hostel, with how many people do you usually move together? [-]'][i];
    g1_var+=(val-g1_mean)**2;
g1_var/=(data['Timestamp'].size);
g1_var=math.sqrt(g1_var);


# In[442]:


g2_mean=0;
g2_var=0;
for i in range(data['Timestamp'].size):
    val=data['How many different friend circles do you have? [-]'][i];
    g2_mean+=val;
g2_mean/=(data['Timestamp'].size);
for i in range(data['Timestamp'].size):
    val=data['How many different friend circles do you have? [-]'][i];
    g2_var+=(val-g2_mean)**2;
g2_var/=(data['Timestamp'].size);
g2_var=math.sqrt(g2_var);


# In[443]:


g3_mean=0;
g3_var=0;
for i in range(data['Timestamp'].size):
    val=data['During weekdays, apart from class hours, 𝗵𝗼𝘄 𝗺𝗮𝗻𝘆 𝗱𝗮𝘆𝘀 𝗶𝗻 𝗮 𝘄𝗲𝗲𝗸 do you usually step out from your hostel?  [-]'][i];
    g3_mean+=val;
g3_mean/=(data['Timestamp'].size);
for i in range(data['Timestamp'].size):
    val=data['During weekdays, apart from class hours, 𝗵𝗼𝘄 𝗺𝗮𝗻𝘆 𝗱𝗮𝘆𝘀 𝗶𝗻 𝗮 𝘄𝗲𝗲𝗸 do you usually step out from your hostel?  [-]'][i];
    g3_var+=(val-g3_mean)**2;
g3_var/=(data['Timestamp'].size);
g3_var=math.sqrt(g3_var);


# In[444]:


g4_mean=0;
g4_var=0;
for i in range(data['Timestamp'].size):
    val=data['During weekdays, apart from class hours, roughly for 𝗵𝗼𝘄 𝗺𝗮𝗻𝘆 𝗵𝗼𝘂𝗿𝘀 do you stay outside your hostel 𝗶𝗻 𝗮 𝗱𝗮𝘆?  [-]'][i];
    g4_mean+=val;
g4_mean/=(data['Timestamp'].size);
for i in range(data['Timestamp'].size):
    val=data['During weekdays, apart from class hours, roughly for 𝗵𝗼𝘄 𝗺𝗮𝗻𝘆 𝗵𝗼𝘂𝗿𝘀 do you stay outside your hostel 𝗶𝗻 𝗮 𝗱𝗮𝘆?  [-]'][i];
    g4_var+=(val-g4_mean)**2;
g4_var/=(data['Timestamp'].size);
g4_var=math.sqrt(g4_var);


# In[445]:


g6_mean=0;
g6_var=0;
for i in range(data['Timestamp'].size):
    val=data['During weekdays, apart from class hours, how many 𝗱𝗶𝗳𝗳𝗲𝗿𝗲𝗻𝘁 𝗽𝗹𝗮𝗰𝗲𝘀 (from the above list) do you usually visit in a 𝘀𝗶𝗻𝗴𝗹𝗲 𝗱𝗮𝘆? [-]'][i];
    g6_mean+=val;
g6_mean/=(data['Timestamp'].size);
for i in range(data['Timestamp'].size):
    val=data['During weekdays, apart from class hours, how many 𝗱𝗶𝗳𝗳𝗲𝗿𝗲𝗻𝘁 𝗽𝗹𝗮𝗰𝗲𝘀 (from the above list) do you usually visit in a 𝘀𝗶𝗻𝗴𝗹𝗲 𝗱𝗮𝘆? [-]'][i];
    g6_var+=(val-g6_mean)**2;
g6_var/=(data['Timestamp'].size);
g6_var=math.sqrt(g6_var);


# In[446]:


g7_mean=0;
g7_var=0;
for i in range(data['Timestamp'].size):
    val=data['How many times do you usually eat out (Canteen/Restaurants/Eateries) 𝗶𝗻 𝗮 𝘄𝗲𝗲𝗸? [-]'][i];
    g7_mean+=val;
g7_mean/=(data['Timestamp'].size);
for i in range(data['Timestamp'].size):
    val=data['How many times do you usually eat out (Canteen/Restaurants/Eateries) 𝗶𝗻 𝗮 𝘄𝗲𝗲𝗸? [-]'][i];
    g7_var+=(val-g7_mean)**2;
g7_var/=(data['Timestamp'].size);
g7_var=math.sqrt(g7_var);


# In[447]:


g9_mean=0;
g9_var=0;
for i in range(data['Timestamp'].size):
    vals=data['Choose the time frames when you usually step out from your hostel during 𝘄𝗲𝗲𝗸𝗲𝗻𝗱𝘀.'][i].split(', ');
    g9_mean+=len(vals);
g9_mean/=(data['Timestamp'].size);
for i in range(data['Timestamp'].size):
    vals=data['Choose the time frames when you usually step out from your hostel during 𝘄𝗲𝗲𝗸𝗲𝗻𝗱𝘀.'][i].split(', ');
    g9_var+=(len(vals)-g9_mean)**2;
g9_var/=(data['Timestamp'].size);
g9_var=math.sqrt(g9_var);


# ## generator

# In[448]:


attributes=['department','hostel','course','year']
def generate_record(attribute_values):
    record=[0,0,0,0,[],0,0,[],[],[],''];
    #1
    k=0;
    for i in attributes:
        record[0]=record[0]+gen1[i][attribute_values[k]]*weights[i];
        k+=1;
    record[0]=max(1,round(np.random.normal(record[0],g1_var)));
        
    #2
    k=0;
    for i in attributes:
        record[1]=record[1]+gen2[i][attribute_values[k]]*weights[i];
        k+=1;
    record[1]=max(1,round(np.random.normal(record[1],g2_var)));  
        
    #3
    k=0;
    for i in attributes:
        record[2]=record[2]+gen3[i][attribute_values[k]]*weights[i];
        k+=1;
    record[2]=min(max(1,round(np.random.normal(record[2],g3_var))),5);
    #4
    k=0;
    for i in attributes:
        record[3]=record[3]+gen4[i][attribute_values[k]]*weights[i];
        k+=1;
    record[3]=max(1,round(np.random.normal(record[3],g4_var)));   
        
    #5
    k=0; temp=0;
    keys=gen5_weights['department'][attribute_values[0]].keys();
    req=dict.fromkeys(keys,0); 
    for i in attributes:
        for j in keys:
            req[j]+=weights[i]*gen5_weights[i][attribute_values[k]][j];
        k+=1;
    record[4]=req; 
        
    #6
    k=0;
    for i in attributes:
        record[5]=record[5]+gen6[i][attribute_values[k]]*weights[i];
        k+=1;
    record[5]=max(0,round(np.random.normal(record[5],g6_var)));
    
    #7
    k=0;
    for i in attributes:
        record[6]=record[6]+gen7[i][attribute_values[k]]*weights[i];
        k+=1;
    record[6]=max(1,round(np.random.normal(record[6],g7_var)));
    
    #8
    k=0;
    keys=gen8_weights['department'][attribute_values[0]].keys();
    req=dict.fromkeys(keys,0); 
    for i in attributes:
        for j in keys:
            req[j]+=weights[i]*gen8_weights[i][attribute_values[k]][j];
        k+=1;
    record[7]=req;
    
    #9
    k=0; cnt=0;
    for i in attributes:
        cnt=cnt+gen9[i][attribute_values[k]]*weights[i];
        k+=1;
    cnt=np.random.normal(cnt,g9_var);
    
    k=0;
    keys=gen9_weights['department'][attribute_values[0]].keys();
    req=dict.fromkeys(keys,0); 
    for i in attributes:
        for j in keys:
            req[j]+=weights[i]*gen9_weights[i][attribute_values[k]][j];
        k+=1;   
    cnt=min(max(round(cnt),1),len(times)-1);
    
    if cnt!=1:
        req['Never']=0;
    
    record[8]=[cnt,req];
        
    #10
    k=0;
    keys=gen10_weights['department'][attribute_values[0]].keys();
    req=dict.fromkeys(keys,0); 
    for i in attributes:
        for j in keys:
            req[j]+=weights[i]*gen10_weights[i][attribute_values[k]][j];
        k+=1;   
    record[9]=req;    
    
    #11
    k=0; temp=0;
    keys=gen11_weights['department'][attribute_values[0]].keys();
    req=dict.fromkeys(keys,0); 
    for i in attributes:
        for j in keys:
            req[j]+=weights[i]*gen11_weights[i][attribute_values[k]][j];
        k+=1;
    record[10]=random.choices(list(req.keys()),list(req.values()))[0];
    return record


# In[449]:


# print(generate_record(['-',43,'UG', '2 nd']))


# In[ ]:




