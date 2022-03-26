from .Campus_Model import Campus

import time
import numpy as np


class Master(Campus):
	"""
	Handles all the initialization and eventually parallelization (if required)

	Args:
		pm                          : Parameters Object
	"""

	def __init__(self, pm):
		self.pm = pm

		self.SIM_DAYS = self.pm.SIM_DAYS

		super().__init__()

	def initiate(self):
		"""
		This function is used to run the simulation
		"""
		# self.initialize_campus()

		self.simulation(start_time=self.pm.SIM_START_TIME)
		# r = list(self.infect_dict.values())
		# print("Average number of people infected by one infectious individual is {}".format(sum(r)/len(r)))

		# self.compare_total_infects()

		# self.generating_input_to_contact_graph_team()

		# return self.Cumulative_Infections_inCampus
		return self.TestingLog["Total Positive"]

	def generating_input_to_contact_graph_team(self):
		"""
		This function is used to store contact matrix after the simulation
		"""
		self.SIM_DAYS = 1
		self.simulation(start_time=self.pm.SIM_START_TIME)
		k = 0
		deg = []
		deg2 = []
		for i in self.all_people:
			deg.append(sum(self.contact_matrix[i.ID]))
			deg2.append(sum(self.sus_contact_matrix[i.ID]))
			if sum(self.contact_matrix[i.ID]) < 90:
				continue
			k+=1
			print(sum(self.contact_matrix[i.ID]), i.Role, i.dept, self.pm.building_name[self.pm.building_id_to_indx[i.residence_building_id]], i.year)
		print("There are a total of {} people who have contacts >= 90".format(k))
		plt.hist(deg,bins=list(np.linspace(0,1000,num=50)))
		plt.title('Degree Distribution')
		plt.xlabel('Degree')
		plt.ylabel('Frequency')
		plt.show()

		plt.hist(deg2,bins=list(np.linspace(0,100,num=50)))
		plt.title('Degree Distribution')
		plt.xlabel('Degree')
		plt.ylabel('Frequency')
		plt.show()
		# with open('identity_table.csv','w', newline='') as fh:
		# 	import csv
		# 	writer = csv.writer(fh)
		# 	writer.writerows([['person_id','person_residence','person_year','person_department','person_age','person_role']]+[[i.ID,self.pm.building_name[self.pm.building_id_to_indx[i.residence_building_id]],i.year,i.dept,i.Age,i.Role] for i in self.all_people])
		# np.savez_compressed('Contact_Matrix',self.contact_matrix)


def StartSimulation(pm):
	# if not pm.is_calibrated:
	# 	dummy = Master(pm)
	# 	dummy.initialize_campus()
	# 	with open('data_'+pm.CampusName+'/Calculated_R0.txt', 'w') as fh:
	# 		fh.write("Calculated_R0={}".format(dummy.calibrate()))
	# 	del(dummy)
	#
	# pm.get_virus_c_value()

	m = Master(pm)
	m.initialize_campus()
	pm.get_virus_c_value(m.calibrate())
	m.TODAY = 1

	# del dummy

	"""
	This instantiates Master Object and starts the simulation
	"""
	# m = Master(pm)
	return m.initiate()
