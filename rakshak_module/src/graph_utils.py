import json
import datetime
import pandas as pd
# import geopy.distance
#import mysql.connector
from .parameters import Contact_Graph_Parameters

CG_pm = Contact_Graph_Parameters()

def decayfunc(time_inf, time_ref):
	"""Return the decayed score for infection."""
	return 1

def proximityfunc(lat1, long1, lat2, long2):
	""" 
	Check two node's cordinates for possibility of infection.  
  
	Parameters: 
	lat1 (decimal):     Latitude coordinate 1
	long1 (decimal):    Longitude coordinate 1
	lat2 (decimal):     Latitude coordinate 2
	long2 (decimal):    Longitude coordinate 2

	Returns: 
	bool:               return 1 and 0 for infection possibility
  
	"""

	threshold= CG_pm.infectdist
	distance=geopy.distance.geodesic((lat1, long1), (lat2,long2)).m
	if (distance <= threshold):
		return 1
	else:
		return 0

def graphformation(time_lower, time_upper):
	""" 
	Function create the overall graph within the selected time window. 
  
	Require two table named identity and activity to retrive the data_IITKGP.
  
	Parameters: 
	time_lower (datetime): Lower time limit
	time_upper (datetime): Upper time limit
  
	Returns: 
	list: return 3 lists i.e edges_list,node_list,title_list
  
	"""
	try:
		db_connection = mysql.connector.connect(
			host      = CG_pm.hostname,
			user      = CG_pm.username,
			passwd    = CG_pm.password,
			database  = CG_pm.dbname
		)
		db_cursor = db_connection.cursor()
	except:
		print("Can't Connect to database, check credentials in parameter file")
	query = ("SELECT * FROM identity ")
	db_cursor.execute(query)
	df1=pd.DataFrame(db_cursor.fetchall())
	df1.columns= ['node','deviceid','student','rollno']
	dict_identity = dict(zip(df1.deviceid, df1.node))
	rev_dict_identity = dict(zip(df1.node, df1.deviceid ))
	query = ("SELECT * FROM activity WHERE time BETWEEN '{}' AND '{}'".format(time_lower,time_upper))  ## incomplete
	db_cursor.execute(query)
	activity_data = pd.DataFrame(db_cursor.fetchall())
	if activity_data.empty==False:
		activity_data.columns=["sl_no","time","node","latitude","longitude"]
	else:
		print("No Activity in the selected Time Window")
		return
	numnodes= len(df1)
	edges= []
	score = {}
	#print(activity_data)
	time_groups = activity_data.groupby('time')
	#with open(r'C:\Users\HP\Desktop\project\Contact_Graph\bluetooth.txt') as json_file:
	#	data1 = json.load(json_file)
	for name, group in time_groups:
		score_tmp = decayfunc(name,time_upper)
		group = group.sort_values('node')
		for i in range(len(group)-1):
			node1 = group.iloc[i,2]
			###########################
			listnearby=[]
			try:
				listnearby = data1[rev_dict_identity[node1]][str(name)]
				listnearby = [dict_identity[i] for i in listnearby if dict_identity[i]>node1]
				for i in listnearby:
					try:
						score[(node1,i)]+=1
					except:
						score[(node1,i)]=1
			except:
				pass
			###########################
			for j in range(i+1,len(group)):
				print("in the third for-loop", i, j)
				node2 =group.iloc[j,2]
				if proximityfunc(group.iloc[i,3],group.iloc[i,4],group.iloc[j,3],group.iloc[j,4]) and node2 not in listnearby:
					try:
						score[(group.iloc[i,2],group.iloc[j,2])]+=1
					except:
						score[(group.iloc[i,2],group.iloc[j,2])]=1
	node_list = list(df1.node)
	title_list = list(df1.deviceid)
	edges_list = []
	for edge,val in score.items():
		edges_list.append((int(edge[0]),int(edge[1]),float(val)))

	return edges_list,node_list,title_list
