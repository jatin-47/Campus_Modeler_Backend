import os
import json
import datetime
import numpy as np
import random
import time
import pandas as pd

from .calibration import distance_dist
from .graph_utils import CG_pm
# from .graph_utils import decayfunc, proximityfunc, graphformation

def get_contacts_from_server(personid, time_datetime, db_conn, begin_time, duration=1):  # have to remove this hardcoding
	"""
	Function print the nodes which came in contact with infected node in past few days.

	Require two table named identity and activity to retrive the data_IITKGP and duration from parameters.

	Parameters:
	deviceid (string): Contains the device id
	time_ref (datetime): Reference time from which we want to check for the past duration days

	Returns:
	None: List of nodes(contacts) and the correspondings edge weights
	"""


	db_cursor = db_conn.cursor()

	# TODO
	'''
	start = time.time()
	query = ("SELECT MIN(time) FROM activity")
	db_cursor.execute(query)
	row = db_cursor.fetchone()
	begin_time=row[0]
	end = time.time()
	print ("Time elapsed to get min time:", end - start)
	'''
	#start = time.time()
	# db_cursor.execute("SELECT unit_id,time FROM activity WHERE time BETWEEN '{}' AND '{}' AND node = {}".format(max(begin_time,time_datetime-datetime.timedelta(days=duration)),time_datetime, personid))
	# units_times = db_cursor.fetchall()  #[(unit_id,time)]
	#end = time.time()
	#print ("Time elapsed to get inf_node's units:", end - start)


	#start = time.time()
	db_cursor.execute("SELECT node FROM activity WHERE node!={} AND (unit_id,time) IN (SELECT unit_id,time FROM activity WHERE time BETWEEN '{}' AND '{}' AND node = {})".format(personid,max(begin_time,time_datetime-datetime.timedelta(days=duration)),time_datetime,personid))
	temp_contacts = [i[0] for i in db_cursor.fetchall()]
	#end = time.time()
	#print("Time elapsed to get execute retriving inf_node's contacts for 24 timestamps at once:", end - start)
	contacts = dict()
	for i in temp_contacts:
		contacts[i] = contacts.get(i,0)+1
	node_list = list(contacts.keys())
	edges_list = []
	for i in node_list:
		edges_list.append(contacts[i])
	# node list should be unique
	# edges = duration of contact


	#print("getting contacts done")



	db_cursor.close()
	return node_list, edges_list

def get_susceptible_contact_matrix(contact_matrix,Unit,calib=False,calib_unit_dict=None,day=None):
	total=len(contact_matrix)
	for t in Unit.visiting:
		l = len(Unit.visiting[t])
		if l == 0 or l==1:
			return

		xi = int((np.pi*(CG_pm.infectdist**2)/Unit.area)*len(Unit.visiting[t]))
		if xi == 0:
			return
		# if Unit.Sector == "Mess":
			# print(xi,l,Unit.Sector)
		mapping = {}
		for i in range(l):
			mapping[i] = Unit.visiting[t][i]
		p = xi*np.ones((l,1), dtype=int)
		A = list(range(0,l))
		for i in range(l):
			if p[i][0] != 0:
				try:
					A.remove(i)
				except:
					pass
				# print(i)
				# print([a for a in list(range(i+1,l)) if p[a][0]!=0],p[i][0], "to choose: {} and total in room: {}".format(xi,l))
				#A = [a for a in list(range(i+1,l)) if p[a][0]!=0]
				lst = random.sample(A,k=min(p[i][0],len(A)))
				p[i][0] = 0
				for x in lst:
					p[x][0] -= 1
					if p[x][0] == 0:
						A.remove(x)
					contact_matrix[mapping[i]][mapping[x]] += 1
					contact_matrix[mapping[x]][mapping[i]] += 1
					if calib:
						calib_unit_dict[day][Unit.Building][Unit.Id]["gamma"][mapping[x]].append(mapping[i])
						calib_unit_dict[day][Unit.Building][Unit.Id]["gamma"][mapping[i]].append(mapping[x])
				# A.remove(i)
		#print(contact_matrix)
	return

def get_susceptible_contact_dict(Unit):
	contact_dict = Unit.unit_contact_dict
	for t in Unit.visiting:
		l = len(Unit.visiting[t])
		if l == 0 or l==1:
			return
		xi = int((np.pi*(CG_pm.infectdist**2)/Unit.area)*len(Unit.visiting[t]))
		if xi == 0:
			return
		# if Unit.Sector == "Mess":
			# print(xi,l,Unit.Sector)
		mapping = {}
		for i in range(l):
			mapping[i] = Unit.visiting[t][i]
		p = xi*np.ones((l,1), dtype=int)
		A = list(range(0,l))
		for i in range(l):
			if p[i][0] != 0:
				try:
					A.remove(i)
				except:
					pass
				# print(i)
				# print([a for a in list(range(i+1,l)) if p[a][0]!=0],p[i][0], "to choose: {} and total in room: {}".format(xi,l))
				#A = [a for a in list(range(i+1,l)) if p[a][0]!=0]
				lst = random.sample(A,k=min(p[i][0],len(A)))
				p[i][0] = 0
				for x in lst:
					p[x][0] -= 1
					if p[x][0] == 0:
						A.remove(x)

					contact_dict[t][mapping[i]].append(mapping[x])
					contact_dict[t][mapping[x]].append(mapping[i])

	return

def contact_tracing(person):
	'''
	Function to do the contact_tracing procedure
	Args:
		person: person object

	Returns:
		contacts,edgeweights he remembers for a specific duration of days

	'''
	contacts, edgweights = [], []
	sz = person.contact_window.qsize()
	while not person.contact_window.empty():
		temp = person.contact_window.get()
		if len(temp) == 0:
			continue
		for j in random.choices(temp,[weight for contact,weight in temp],k=round(len(temp)/(sz))):
			contacts.append(j[0])
			edgweights.append(j[1])
		sz-=1

	return contacts,edgweights

def get_contacts_from_unit_contact_dicts(person):
	temp_contacts = []
	distances = []
	# for person in all_people:
	# 	if person.ID == personid:
	# 		continue
	# 	for tmstamp in person.today_schedule:
	# 		if person.today_schedule[tmstamp] == all_people[personid].today_schedule[tmstamp]:
	# 			temp_contacts.append(person.ID)
	for tmstamp in person.today_schedule:
		# if tmstamp not in person.today_schedule[tmstamp].visiting or person.today_schedule[tmstamp].visiting[tmstamp] is None:
		# 	print(tmstamp)
		# 	print(person.today_schedule[tmstamp].visiting)
		# 	print(person.today_schedule[tmstamp].Sector)

		try:
			if person.today_schedule[tmstamp].Id == -1:
				continue
			# person.today_schedule[tmstamp].calc_interperson_distance()
			# print(tmstamp,person.today_schedule[tmstamp].area, len(person.today_schedule[tmstamp].visiting[tmstamp]), person.today_schedule[tmstamp].Building,[j for j in list(person.today_schedule[tmstamp].interpersonDist.items()) if j[1] != None])
			# person.today_schedule[tmstamp].calc_interperson_distance2()
			# print(tmstamp,person.today_schedule[tmstamp].area, len(person.today_schedule[tmstamp].visiting[tmstamp]), person.today_schedule[tmstamp].Building,[j for j in list(person.today_schedule[tmstamp].interpersonDist.items()) if j[1] != person.today_schedule[tmstamp].area])
			# print()
			# person.today_schedule[tmstamp].fill_unit_contact_dict()
			temp = person.today_schedule[tmstamp].unit_contact_dict[tmstamp][person.ID]
			temp_contacts.extend(temp)
			distances.extend([person.today_schedule[tmstamp].interpersonDist[tmstamp]]*len(temp))
		except:
			print(tmstamp, person.inCampus, person.ID, person.today_schedule[tmstamp].unit_contact_dict, person.today_schedule[tmstamp].interpersonDist, person.today_schedule[tmstamp].Sector, person.today_schedule[tmstamp].Id, person.residence_unit.Id, person.Status, person.State)
			assert 1 == 0

	prob_transmisson = dict()
	k = 0
	for i in temp_contacts:
		if distance_dist(person.Campus.pm,distances[k]) > 1:
			print("Probability transmission greater than 1")
			assert 1==0
		prob_transmisson[i] = 1-(1-prob_transmisson.get(i,0))*(1-distance_dist(person.Campus.pm,distances[k]))
		k+=1
	node_list = list(prob_transmisson.keys())
	edges_list = []
	for i in node_list:
		edges_list.append(prob_transmisson[i])
	# print(prob_transmisson)

	# print(node_list)


	return node_list, edges_list

def get_contacts_without_using_server(person):
	# c = 0.08295785211044983
	# c = 0.010547400051779413
	# c = 0.08080028010941248
	# c = 0.005497283066266391
	# c = 0.005599476863146552
	# c = 0.0037153147652850193
	# c = 0.04289581288159128
	c = 0.01612367453657153
	mat = person.Campus.daily_contact_matrix
	temp_contacts = []
	distances = []
	# for person in all_people:
	# 	if person.ID == personid:
	# 		continue
	# 	for tmstamp in person.today_schedule:
	# 		if person.today_schedule[tmstamp] == all_people[personid].today_schedule[tmstamp]:
	# 			temp_contacts.append(person.ID)
	for tmstamp in person.today_schedule:
		# if tmstamp not in person.today_schedule[tmstamp].visiting or person.today_schedule[tmstamp].visiting[tmstamp] is None:
		# 	print(tmstamp)
		# 	print(person.today_schedule[tmstamp].visiting)
		# 	print(person.today_schedule[tmstamp].Sector)

		try:
			person.today_schedule[tmstamp].calc_interperson_distance()
			# print(tmstamp,person.today_schedule[tmstamp].area, len(person.today_schedule[tmstamp].visiting[tmstamp]), person.today_schedule[tmstamp].Building,[j for j in list(person.today_schedule[tmstamp].interpersonDist.items()) if j[1] != None])
			# person.today_schedule[tmstamp].calc_interperson_distance2()
			# print(tmstamp,person.today_schedule[tmstamp].area, len(person.today_schedule[tmstamp].visiting[tmstamp]), person.today_schedule[tmstamp].Building,[j for j in list(person.today_schedule[tmstamp].interpersonDist.items()) if j[1] != person.today_schedule[tmstamp].area])
			# print()
			temp = [i for i in person.today_schedule[tmstamp].visiting[tmstamp] if i!=person.ID]
			temp_contacts.extend(temp)
			distances.extend([person.today_schedule[tmstamp].interpersonDist[tmstamp]]*len(temp))
		except:
			print(tmstamp, person.ID, person.today_schedule[tmstamp].visiting, person.today_schedule[tmstamp].Sector)
			assert 1 == 0
	temp_contacts2 = []
	distances2 = []
	k = 0
	for i in temp_contacts:
		if mat[person.ID][i]<1:
			continue
		temp_contacts2.append(i)
		distances2.append(distances[k])
		k+=1

	prob_transmission = dict()
	k = 0
	for i in temp_contacts2:
		if c*distance_dist(person.Campus.pm,distances2[k]) > 1:
			print("Probability transmission greater than 1")
			assert 1==0
		prob_transmission[i] = prob_transmission.get(i,0)+c*distance_dist(person.Campus.pm,distances2[k])
		# prob_transmisson[i] = 1-(1-prob_transmisson.get(i,0))*(1-c*distance_dist(person.Campus.pm,distances2[k]))
		# print(prob_transmission[i],distances2[k])
		k+=1
	node_list = list(prob_transmission.keys())
	edges_list = []
	for i in node_list:
		edges_list.append(prob_transmission[i])
	# print(prob_transmisson)

	# print(node_list)


	return node_list, edges_list


