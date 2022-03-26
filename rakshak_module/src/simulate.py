import os
import csv
import time
import json
import random
import datetime
import numpy as np

import pandas as pd

from .contact_graph import get_susceptible_contact_matrix, contact_tracing
from .graph_utils import CG_pm
from .person import visitor

from .statemachine import TestingState
from .utils import func_timer

class Initialization:
	"""
	Initializes the Campus Model according to the DAY 0 case statistics given
	"""
	def __init__(self):

		self.asymptomatic, self.symptomatic, self.recovered, self.partially_vaccinated, self.fully_vaccinated = self.pm.init_case_statistics.get("Asymptomatic", 0), self.pm.init_case_statistics.get("Symptomatic",0), self.pm.init_case_statistics.get("Recovered",0), self.pm.init_case_statistics.get("Partially_Vaccinated",0), self.pm.init_case_statistics.get("Fully_Vaccinated",0)

		temp = [i for i in self.all_people if i.Status == 'Free']
		sample_persons = list(np.random.choice(temp,size=self.asymptomatic+self.symptomatic+self.recovered+self.partially_vaccinated+self.fully_vaccinated,replace=False))

		self.init_asymptomatic(sample_persons)
		self.init_symptomatic(sample_persons)
		self.init_recovered(sample_persons)
		self.init_partially_vaccinated(sample_persons)
		self.init_fully_vaccinated(sample_persons)



class Simulate():
	def __init__(self):

		# Building Statistics
		self.building_occupancy = {}
		self.building_occupancy_infected = {}

		# Case Statistics
		self.DailyInfections = []
		self.TotalActive     = []
		self.Cumulative_Infections = []
		self.TotalActive_inCampus = []
		self.Cumulative_Infections_inCampus = []

		self.TestingLog = {"Date of Testing":[],
						   "Number of Tests": [],
						   "Number of Student's Tested": [],
						   "Total Positive": [],
						   "No of Student Positive": []}

		# Saving Results
		self.SimName = self.pm.SimName
		self.SAVEDIR = self.pm.SAVEDIR
		self.hostel_occupancy = {}

		self.SIMULATE        = True
		self.TODAY           = 1
		self.Lockdown        = 0

		super().__init__()

		self.fieldnames = ["Healthy",
						   "Asymptomatic",
						   "Symptomatic",
						   "Recovered",
						   "Died",
						   "Daily_positive_tested",
						   "Cumulative_positive_tested",
						   "Not_vaccinated",
						   "Partially_vaccinated",
						   "Fully_vaccinated",
						   "DailyNewInfections",
						   "CumulativeInfections"]

		with open(os.path.join(self.SAVEDIR, 'results.csv'), 'w', newline='') as csv_file:
			csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
			csv_writer.writeheader()

		self.fieldnames2 = ["Day", "Hour"]
		for i in self.pm.building_name:
			self.fieldnames2.append(str(i))
		with open(os.path.join(self.SAVEDIR, 'Building_occupancy.csv'), 'w', newline='') as csv_file:
			csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames2)
			csv_writer.writeheader()

		self.fieldnames3 = ["Day", "Hour"]
		for i in self.pm.polygons:
			self.fieldnames3.append(str(i)[10:-2])
		with open(os.path.join(self.SAVEDIR, 'Hotspots.csv'), 'w', newline='') as csv_file:
			csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames3)
			csv_writer.writeheader()

		self.fieldnames4 = ['day','hour','id','x','y','state','role','is_atRisk', 'vaccination_state']
		with open(os.path.join(self.SAVEDIR, 'locations.csv'), 'w', newline='') as csv_file:
			csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames4)
			csv_writer.writeheader()

		self.total_hours_of_interaction_avg_distance = {}

		self.infect_dict = {}

	def calibrate(self,start_time=None):

		self.start_time = start_time
		if start_time is None:
			curr = time.localtime()
			self.start_time = time.struct_time((curr.tm_year,curr.tm_mon,curr.tm_mday,0,0,0,curr.tm_wday,curr.tm_yday,curr.tm_isdst))
		self.curr_timestamp = self.start_time

		RperDay = 0

		while (self.SIMULATE):

			print("calibrating for the timestamp",time.strftime("%a, %d %b %Y %H:%M:%S +0000", self.curr_timestamp))

			self.__update_movement_time_series__()
			self.__generate_contacts__()
			self.no_people_inf_by_person = {}
			for p in self.all_people:
				try:
					contacts_idx, edge_weights = self.__get_contacts__(p)
				except:
					edge_weights = []
				self.no_people_inf_by_person[p.ID] = sum([1 for edge in edge_weights if random.choices([True, False], weights=[edge, 1-edge])[0]])
			self.__building_random_transmissions__(calibrate=1)
			RperDay += sum([value[1] for value in self.no_people_inf_by_person.items()])/len(self.no_people_inf_by_person) # Avg no of people infected by each person directly

			self.curr_timestamp = time.localtime(time.mktime(self.start_time) + self.TODAY * 24 * 60 * 60)
			self.TODAY += 1

			if self.TODAY > 7:
				RperDay/=7
				EDays 	= np.average(self.pm.Virus_IncubationPeriod,weights=self.pm.Population_Dist)

				print("-------------------------Calibration done-------------------------- Calculated_R0 =",RperDay*EDays)
				return RperDay*EDays



	def simulation(self, start_time=None):
		"""
		Main function to set up the simulation, simulate each day and save the results
		"""

		# self.contact_matrix = np.zeros((len(self.all_people),len(self.all_people)), dtype=float)
		# self.contact_matrix = np.zeros((len(self.all_people),len(self.all_people)), dtype=int)
		# self.sus_contact_matrix = np.zeros((len(self.all_people),len(self.all_people)), dtype=int)

		# Set sim start day
		self.start_time = start_time
		if start_time is None:
			curr = time.localtime()
			self.start_time = time.struct_time((curr.tm_year,curr.tm_mon,curr.tm_mday,0,0,0,curr.tm_wday,curr.tm_yday,curr.tm_isdst))


		# Establish database connection
		# self.db_conn = create_db_publish_locations()
		#publish_identity(self.all_people, self.db_conn)
		self.curr_timestamp = self.start_time

		self.city_prevalence_rates = None

		# Simulation loop
		while (self.SIMULATE):
			# self.daily_contact_matrix = np.zeros((len(self.all_people),len(self.all_people)), dtype=int)

			if self.pm.Verbose:
				print("Simulating Day {}".format(self.TODAY))
			self.__simulate_day__()

			self.__set_risk_to_zero__()
			# print([i.risk for i in self.all_people[:50]])

			# print([i.ID for i in self.HQuarantinedP])
			# print([i.ID for i in self.AFreeP])
			# print([i.ID for i in self.AQuarantinedP])
			# print([i.ID for i in self.SIsolatedP])
			# print([i.ID for i in self.SHospitalizedP])
			# print([i.ID for i in self.SIcuP])
			# print([i.ID for i in self.RRecoveredP])
			# print([i.ID for i in self.RDiedP])
			# print([i.ID for i in self.SFreeP])

			#if self.TODAY%self.pm.duration == 0:
			#TODO: clear activity table
			#    pass


			# print(self.all_people[0].contact_window)
			# print(contact_tracing(self.all_people[0],self.TODAY-1))
			if self.TODAY > self.SIM_DAYS:
				self.SIMULATE = False
				# self.plot_positive_cases()

	def __intervention__(self):

		criteria = {1:len(self.PositivePlaceholder[self.TODAY-2]),
					2:lambda n:sum([len(i) for i in self.PositivePlaceholder[n:self.TODAY-1]]),
					3:self.TestingQueue.qsize()}


		#     print("--------------------------------------------------Lockdown-------------------------------------")

		for sector in self.pm.shutdown_strategy['sectors']:
			start_criterion = self.pm.shutdown_strategy['sectors'][sector]['start_criterion']
			end_criterion = self.pm.shutdown_strategy['sectors'][sector]['end_criterion']

			if start_criterion[0] == 0:
				self.sectors[sector].lift_lockdown()
				continue

			start_threshold = start_criterion[1]
			end_threshold = end_criterion[1]

			if type(start_criterion[0]) == list:
				n = self.TODAY- start_criterion[0][1]
				if n<0:
					n=0
				start_condition = criteria[start_criterion[0][0]](n)
			else:
				start_condition = criteria[start_criterion[0]]

			if type(end_criterion[0]) == list:
				end_condition = criteria[end_criterion[0][0]](end_criterion[0][1])
			else:
				end_condition = criteria[end_criterion[0]]

			if not self.sectors[sector].Shutdown_duration == 0:
				self.sectors[sector].Shutdown_duration -= 1

			if start_condition >= start_threshold:
				self.sectors[sector].impose_lockdown(
					duration            = self.pm.shutdown_strategy['sectors'][sector]['duration'],
					roles_restricted    = self.pm.shutdown_strategy['sectors'][sector]['roles']
				)
			elif self.sectors[sector].Shutdown_duration == 0 or end_condition < end_threshold:
				self.sectors[sector].lift_lockdown()



	def __simulate_day__(self):
		"""
		Simulate one day
		"""
		# TODO (later): Lockdown checks go here
		# TODO (later): Travel to and from campus goes here
		# TODO (later): CR and IFP Phases
		# TODO (later): Daily Transactions (TechM + Outside campus travel)


		TestingState.Num_not_tested = 0

		self.all_people = []
		for i in self.Total_people:
			if i.inCampus:
				self.all_people.append(i)
				if (i.state == "Not_tested" or i.re_test == 1) :
					TestingState.Num_not_tested += 1

		if self.TODAY == 1:
			Initialization.__init__(self)
		# print("---------------------------------------------------------------------------------",TestingState.Num_not_tested)

		if self.pm.Verbose: print("No.of people in Campus: {}".format(len(self.all_people)))


		self.__intervention__()


		self.__update_visitors__()
		self.infect_outsiders()                  # infecting outsiders who come from outside


		self.__update_movement_time_series__()

		# for p in self.Students:
		# 	for day in p.timetable:
		# 		for t in p.timetable[day]:
		# 			if p.timetable[day][t] != p.residence_unit and p.timetable[day][t].Sector != "Mess":
		# 				print(p.ID, day, t, p.timetable[day][t].Sector)


		self.__risk_assigning__()

		# self.__update_today_movements__()
		if (self.pm.SaveMovementSnapshots):
			self.__save_today_movements_snapshots__(day_interval=1)

		# self.__get_contact_matrix2__(isdaily=True)
		self.__generate_contacts__()

		if self.pm.testing_strategy == 3:
			self.update_contact_window()

		self.daily_transmissions()

		self.daily_vaccination()

		self.daily_testing()




		self.__save_results__()

		if self.pm.Verbose:
			print('----------')
			print()

		self.NewInfection=0

		# self.__get_contact_matrix__()
		# self.__get_contact_matrix2__()


		self.curr_timestamp = time.localtime(time.mktime(self.start_time)+(self.TODAY)*24*60*60)

		self.TODAY += 1

	@func_timer
	def __generate_contacts__(self):
		for building in self.Units_Placeholder:
			for unit in self.Units_Placeholder[building]:
				self.Units_Placeholder[building][unit].calc_interperson_distance()
				self.Units_Placeholder[building][unit].fill_unit_contact_dict()

	def __get_contact_matrix__(self):
		for person in self.all_people:
			contacts, frequencies = self.__get_contacts__(person)
			for i in range(len(contacts)):
				# if self.TODAY > 14:
				#     self.contact_matrix[person.ID,contacts[i]] *= 0.7
				# self.contact_matrix[person.ID,contacts[i]] += frequencies[i]
				self.contact_matrix[person.ID,contacts[i]] = 1

	def __get_contact_matrix2__(self,isdaily=False):
		if isdaily==False:
			for building in self.Units_Placeholder:
				for unit in self.Units_Placeholder[building]:
					get_susceptible_contact_matrix(self.sus_contact_matrix,self.Units_Placeholder[building][unit])
		else:
			for building in self.Units_Placeholder:
				for unit in self.Units_Placeholder[building]:
					get_susceptible_contact_matrix(self.daily_contact_matrix,self.Units_Placeholder[building][unit])

	@func_timer
	def __save_results__(self):
		"""
		Save case stats etc. to file instead of printing
		"""

		if self.pm.Verbose:
			print('----------')
		self.healthy, self.asymptomatic, self.symptomatic, self.recovered, self.died = 0, 0, 0, 0, 0
		self.not_vaccinated = 0
		self.partially_vaccinated = 0
		self.fully_vaccinated = 0

		self.healthy_inCampus, self.asymptomatic_inCampus, self.symptomatic_inCampus, self.recovered_inCampus, self.died_inCampus = 0, 0, 0, 0, 0
		self.not_vaccinated_inCampus = 0
		self.partially_vaccinated_inCampus = 0
		self.fully_vaccinated_inCampus = 0

		for s in self.Total_people:
			if s.State == "Healthy":
				self.healthy+=1
				if s.inCampus:
					self.healthy_inCampus+=1
			elif s.State == 'Asymptomatic':
				self.asymptomatic+=1
				if s.inCampus:
					self.asymptomatic_inCampus+=1
			elif s.State == 'Symptomatic':
				self.symptomatic+=1
				if s.inCampus:
					self.symptomatic_inCampus+=1
			elif s.State == 'Recovered':
				self.recovered+=1
				if s.inCampus:
					self.recovered_inCampus+=1
			else:
				self.died+=1
				if s.inCampus:
					self.died_inCampus+=1

			if s.Vaccination_State == "Not_Vaccinated":
				self.not_vaccinated += 1
				if s.inCampus:
					self.not_vaccinated_inCampus+=1
			elif s.Vaccination_State == "Partially_Vaccinated":
				self.partially_vaccinated += 1
				if s.inCampus:
					self.partially_vaccinated_inCampus+=1
			elif s.Vaccination_State == "Fully_Vaccinated":
				self.fully_vaccinated += 1
				if s.inCampus:
					self.fully_vaccinated_inCampus+=1

		self.DailyInfections.append(self.NewInfection)
		self.TotalActive.append(self.asymptomatic+self.symptomatic)
		self.Cumulative_Infections.append(self.asymptomatic+self.symptomatic+self.recovered)

		self.TotalActive_inCampus.append(self.asymptomatic_inCampus+self.symptomatic_inCampus)
		self.Cumulative_Infections_inCampus.append(self.asymptomatic_inCampus+self.symptomatic_inCampus+self.recovered_inCampus)





		if (self.TODAY==self.SIM_DAYS):

			pd.DataFrame.from_dict(self.TestingLog).to_csv(os.path.join(self.SAVEDIR, 'TestResults.csv'),index=False)

		if self.pm.Verbose:
			print("Persons whose State is Healthy: ", self.healthy)
			print("Persons whose State is Asymptomatic: ", self.asymptomatic)
			print("Persons whose State is Symptomatic: ", self.symptomatic)
			print("Persons whose State is Recovered: ", self.recovered)
			print("Persons whose State is Died: ", self.died)
			print("Persons whose Vaccination State is Partially_Vaccinated: ", self.partially_vaccinated)
			print("Persons whose Vaccination State is Fully_Vaccinated: ", self.fully_vaccinated)
			print("Total active cases", self.TotalActive)
			print("Daily new infections", self.DailyInfections)
			print("Daily new positive cases: ", [len(self.PositivePlaceholder[i]) for i in range(len(self.PositivePlaceholder[:self.TODAY]))])
			print()

		self.__update_building_occupancy__()
		self.__update_building_occupancy_infected__()

		r = {}
		for t in range(24):
			r[t] = {}
			for building_id in self.Units_Placeholder:
				r[t][building_id] = 0

		for building_id in self.Units_Placeholder:
			for unit_id in self.Units_Placeholder[building_id]:
				for t in self.Units_Placeholder[building_id][unit_id].visiting:
					r[t][building_id] += len(self.Units_Placeholder[building_id][unit_id].visiting[t])

		self.building_occupancy[self.TODAY] = r

		with open(os.path.join(self.SAVEDIR, 'results.csv'), 'a', newline='') as csv_file:
			csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
			info = {
				"Healthy": self.healthy,
				"Asymptomatic": self.asymptomatic,
				"Symptomatic": self.symptomatic,
				"Recovered": self.recovered,
				"Died": self.died,
				"Daily_positive_tested": len(self.PositivePlaceholder[self.TODAY-1]),
				"Cumulative_positive_tested": sum([len(i) for i in self.PositivePlaceholder]),
				"Not_vaccinated": self.not_vaccinated,
				"Partially_vaccinated": self.partially_vaccinated,
				"Fully_vaccinated": self.fully_vaccinated,
				"DailyNewInfections": self.DailyInfections[-1],
				"CumulativeInfections": self.Cumulative_Infections[-1]
			}

			csv_writer.writerow(info)


		with open(os.path.join(self.SAVEDIR, 'Building_occupancy.csv'), 'a', newline='') as csv_file:
			csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames2)
			for i in range(24):
				info = {"Day": self.TODAY,"Hour": i}
				info.update({self.pm.building_name[self.pm.building_id_to_indx[building]]:self.building_occupancy[self.TODAY][i][building] for building in self.building_occupancy[self.TODAY][i]})

				csv_writer.writerow(info)

		with open(os.path.join(self.SAVEDIR, 'Hotspots.csv'), 'a', newline='') as csv_file:
			csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames3)
			for i in range(24):
				info = {"Day": self.TODAY,"Hour": i}
				info.update({str(self.pm.polygons[self.pm.building_id_to_indx[building]])[10:-2]:self.building_occupancy_infected[self.TODAY][i][building] for building in self.building_occupancy_infected[self.TODAY][i]})

				csv_writer.writerow(info)

		if self.is_validation_sim:
			date = time.strftime("%m/%d/%Y",self.curr_timestamp)
			self.hostel_occupancy[date] = {self.pm.building_name[self.pm.building_id_to_indx[k]]: 0 for k in self.sectors["Residence"].non_occupied_rooms["Student Residence"]}
			for i in self.all_people:
				if i.Role != "student":
					continue
				bldg_id = i.today_schedule[3].Building  # at 3am most of them will likely stay in their residence or quarantine/isolation centre
				bldg_name = self.pm.building_name[self.pm.building_id_to_indx[bldg_id]]
				if self.hostel_occupancy[date].get(bldg_name,-1) == -1:
					continue
				self.hostel_occupancy[date][bldg_name] += 1
			if self.TODAY == self.SIM_DAYS:
				pd.DataFrame.from_dict(self.hostel_occupancy).to_csv(os.path.join(self.SAVEDIR, 'HostelStudentCount.csv'))

		# if self.TODAY == 30:
		#     with open("hourwise_building.json", 'w') as fp:
		#         json.dump(self.building_occupancy, fp, sort_keys=True, indent=3)

		infected_list = list(self.infect_dict.values())
		# try:
		#     print("Average number of people infected by one infectious individual is {}".format(sum(infected_list)/len(infected_list)))
		# except:
		#     pass


	def __update_building_occupancy__(self):
		r = {}
		for t in range(24):
			r[t] = {}
			for building_id in self.Units_Placeholder:
				r[t][building_id] = 0

		for building_id in self.Units_Placeholder:
			for unit_id in self.Units_Placeholder[building_id]:
				for t in self.Units_Placeholder[building_id][unit_id].visiting:
					r[t][building_id] += len(self.Units_Placeholder[building_id][unit_id].visiting[t])
		self.building_occupancy[self.TODAY] = r

	def __update_building_occupancy_infected__(self):
		r = {}
		for t in range(24):
			r[t] = {}
			for building_id in self.Units_Placeholder:
				r[t][building_id] = 0

		for p in self.AFreeP:
			for t in p.today_schedule:
				if p.today_schedule[t].Id == -1:
					continue
				r[t][p.today_schedule[t].Building]+=1

		for p in self.AQuarantinedP:
			for t in p.today_schedule:
				if p.today_schedule[t].Id == -1:
					continue
				r[t][p.today_schedule[t].Building] +=1

		for p in self.SIsolatedP:
			for t in p.today_schedule:
				if p.today_schedule[t].Id == -1:
					continue
				r[t][p.today_schedule[t].Building] +=1

		for p in self.SHospitalizedP+self.SIcuP:
			for t in p.today_schedule:
				if p.today_schedule[t].Id == -1:
					continue
				r[t][p.today_schedule[t].Building] +=1

		self.building_occupancy_infected[self.TODAY] = r


	def __update_today_movements__(self):
		"""
		Publish today's movements in the MySQL server
		"""
		tmstamps = list(self.all_people[0].today_schedule.keys())
		for tmstamp in tmstamps:
			publish_activity(self.all_people, tmstamp, self.db_conn)

	def __building_shutdown__(self, Buildingid):
		"""
		When Building is shutdown
		"""
		roles = self.buildings[Buildingid].roles_restricted
		time_in_sec = time.mktime(self.curr_timestamp)
		for i in self.buildings[Buildingid].Building_units_list:
			for t in self.buildings[Buildingid].Building_units_list[i].visiting:
				temp = self.buildings[Buildingid].Building_units_list[i].visiting[t].copy()
				for id in temp :
					if self.ID_to_person[id].Role in roles:                                     #
						# print(t)
						# print(self.all_people[id].today_schedule[t])
						# print(self.sectors[sectorname].Units_list[i][j])
						if self.ID_to_person[id].today_schedule[t].Building != Buildingid:
							continue
						self.ID_to_person[id].today_schedule[t].visiting[t].remove(id)
						self.ID_to_person[id].today_schedule[t] = self.ID_to_person[id].residence_unit
						if self.ID_to_person[id].residence_unit.visiting.get(t,-1) == -1:
							self.ID_to_person[id].residence_unit.visiting[t] = []
						self.ID_to_person[id].residence_unit.visiting[t].append(id)

	def __sector_shutdown__(self,sectorname):
		"""
		When sector is shutdown
		"""

		roles = self.sectors[sectorname].roles_restricted
		for i in self.sectors[sectorname].building_ids:
			for j in self.sectors[sectorname].Units_list[i]:
				for t in self.sectors[sectorname].Units_list[i][j].visiting:
					temp = self.sectors[sectorname].Units_list[i][j].visiting[t].copy()
					for id in temp :
						if self.ID_to_person[id].Role in roles:
							# print(t)
							# print(self.all_people[id].today_schedule[t])
							# print(self.sectors[sectorname].Units_list[i][j])
							if self.ID_to_person[id].today_schedule[t].Sector != sectorname:
								continue
							self.ID_to_person[id].today_schedule[t].visiting[t].remove(id)
							self.ID_to_person[id].today_schedule[t] = self.ID_to_person[id].residence_unit
							if self.ID_to_person[id].residence_unit.visiting.get(t,-1) == -1:
								self.ID_to_person[id].residence_unit.visiting[t] = []
							self.ID_to_person[id].residence_unit.visiting[t].append(id)






	def __isolate_students(self, person, timestamp):
		if person.Isolation_Days == 0:
			if person.State == person.states[2]:     #14 days extend again for symptomatic person if retesting doesn't exist
				person.Isolation_Days = self.pm.Quarantine_Period
			else:
				person.free_Qcentre()


		if person.Q_unit == -1 :
			#print("in func", person.ID,person.State, person.Status)
			todays_timestamps = list(range(24))
			bldg_id=-1
			unit_id=-1
			if person.Role=='student':
				if person.state == "Tested_Positive":
					temp = self.quarantine_centre_ids
				else:
					temp = self.isolation_centre_ids
				if len(temp) != 0:
					for i in random.sample(temp,k=1):
						if len(self.sectors["Residence"].non_occupied_rooms["Student Residence"][i])!=0:
							bldg_id=i
							unit_id=random.choice(self.sectors["Residence"].non_occupied_rooms["Student Residence"][i])
							self.sectors["Residence"].non_occupied_rooms["Student Residence"][i].remove(unit_id)
					if bldg_id!=-1:
						person.today_schedule=dict.fromkeys(todays_timestamps, self.Units_Placeholder[bldg_id][unit_id])
						person.Q_building=bldg_id
						person.Q_unit=self.Units_Placeholder[bldg_id][unit_id]

			if bldg_id == -1 or person.Role in ['faculty','staff','desk_worker','non_desk_worker']:
				person.today_schedule = dict.fromkeys(todays_timestamps, person.residence_unit)

				person.Q_unit = person.residence_unit
				person.Q_building = person.residence_building_id

		day = time.strftime("%A",time.localtime(timestamp)).casefold()
		for t in range(24):
			if person.Q_unit.visiting.get(t,-1) == -1:
				person.Q_unit.visiting[t] = []
			person.Q_unit.visiting[t].append(person.ID)

			if type(person.timetable[day][t]) == dict:
				continue
			if person.timetable[day][t] == person.residence_unit:
				continue
			person.timetable[day][t].visiting[t].remove(person.ID)

		person.Isolation_Days = person.Isolation_Days-1


		if person.State == "Recovered":
			person.free_Qcentre()
			person.Status = "Free"
			person.Isolation_Days = 0



	@func_timer
	def __update_movement_time_series__(self):
		"""
		Updates each person.today_schedule to a dictionary containing the timestamps of a given date and locations
		"""
		time_in_sec = time.mktime(self.curr_timestamp)

		hall_ids = list(map(int,list(self.pm.df[self.pm.df["BuildingType"]=="Student Residence"].loc[:, "BuildingID"])))
		dep_ids = list(map(int,list(self.pm.df[self.pm.df["BuildingType"]=="Academic"].loc[:, "BuildingID"])))

		day = time.strftime("%A",time.localtime(time_in_sec)).casefold()

		# start = time.time()
		for i in self.Units_Placeholder:
			for j in self.Units_Placeholder[i]:
				self.Units_Placeholder[i][j].visiting = {k: [id for id in self.Units_Placeholder[i][j].default_visiting[day][k] if self.ID_to_person[id].inCampus] for k in self.Units_Placeholder[i][j].default_visiting[day]}

		for person in self.all_people:
			timestamp = time_in_sec
			todays_timestamps = list(range(24))

			if person.Status == 'Quarantined' or person.Status == 'Isolation':

				if person.Isolation_Days == 0:
					if person.State == person.states[2]:  # 14 days extend again for symptomatic person if retesting doesn't exist
						person.Isolation_Days = person.Campus.pm.Quarantine_Period
					else:
						person.free_Qcentre()
						person.free()

				if person.Isolation_Days > 0:
					self.__isolate_students(person, timestamp)

			if person.Status == 'Free':
				person.today_schedule = person.timetable[day].copy()
				# if person.Role != "student":
				#     continue
				# continue
				for j in person.final_times[day]:
					# temp = timestamp + j*60*60
					# if type(person.timetable[time.strftime("%A",time.localtime(temp)).casefold()][j])==dict:
					# if len(person.timetable[time.strftime("%A",time.localtime(temp)).casefold()][j1]) == 0:
						# print("yes it is still zero", time.strftime("%A",time.localtime(temp)).casefold(), j1, person.personID)
					# if list(person.timetable[time.strftime("%A",time.localtime(timestamp)).casefold()][j].values()) == [0.0]:
					#     print(list(person.timetable[time.strftime("%A",time.localtime(timestamp)).casefold()][j].keys()),list(person.timetable[time.strftime("%A",time.localtime(timestamp)).casefold()][j].values()))
					try:
						bldg_id=random.choices(list(person.timetable[day][j].keys()), list(person.timetable[day][j].values()))[0]
					except:
						print(person.ID,day,j,person.final_times[day],person.Role,person.timetable[day])
						assert 1==0
					if bldg_id == 'Other Hall of Residence' or bldg_id == "Student's Hostel":
						while 1:
							bldg_id=random.choice(hall_ids)
							if bldg_id != person.residence_building_id:
								break
					elif bldg_id == 'A Department':
						bldg_id=random.choice(dep_ids)
					elif bldg_id == "Type B- park":
						bldg_id= random.choice([59,60,61])  # these are the building_ids of the three type B parks available in IITJ campus
					unt_id = random.choice(list(self.Units_Placeholder[bldg_id].keys()))
					person.today_schedule[j] = self.Units_Placeholder[bldg_id][unt_id]

					if person.Role == "faculty" or person.Role == "staff":
						if self.Units_Placeholder[bldg_id][unt_id].Sector in ["Market","Restaurant","Grounds","Gymkhana"]:
							for fam in person.Family_list_obj:
								fam.today_schedule[j] = self.Units_Placeholder[bldg_id][unt_id]
					# self.Units_Placeholder[bldg_id][unt_id].visiting[j].append(person.ID)
					if self.Units_Placeholder[bldg_id][unt_id].visiting.get(j,-1) == -1:
						self.Units_Placeholder[bldg_id][unt_id].visiting[j] = []
					self.Units_Placeholder[bldg_id][unt_id].visiting[j].append(person.ID)
					# print(self.Units_Placeholder[bldg_id][unt_id].visiting, "final_times: {}".format(j))

					# else:
					#     newschedule[time.localtime(temp)] = person.timetable[time.strftime("%A",time.localtime(temp)).casefold()][j]
					#     if person.timetable[time.strftime("%A",time.localtime(temp)).casefold()][j].visiting.get(time.localtime(temp),None) is None:
					#         person.timetable[time.strftime("%A",time.localtime(temp)).casefold()][j].visiting[time.localtime(temp)] = [person.ID]
					#     else:
					#         person.timetable[time.strftime("%A",time.localtime(temp)).casefold()][j].visiting[time.localtime(temp)].append(person.ID)





			else:
				# if person.in_hospital == True:
				#     continue
				if person.Status == 'Hospitalized' or person.Status == 'ICU':
					if person.in_hospital != True:
						building_id = person.Campus.sectors['Healthcare'].building_ids[0]
						unit_id = random.choice(list(person.Campus.sectors['Healthcare'].Units_list[building_id].keys()))
						person.today_schedule = dict.fromkeys(todays_timestamps,self.sectors['Healthcare'].Units_list[building_id][unit_id])
						person.in_hospital = True

					for t in range(24):
						if person.today_schedule[t].visiting.get(t, -1) == -1:
							person.today_schedule[t].visiting[t] = []
						person.today_schedule[t].visiting[t].append(person.ID)

						if type(person.timetable[day][t]) == dict:
							continue
						if person.residence_unit.Id != -1:
							person.timetable[day][t].visiting[t].remove(person.ID)

				#building_id = person.Campus.sectors['Healthcare'].building_ids[0]
				#unit_id = random.choice(list(person.Campus.sectors['Healthcare'].Units_list[building_id].keys()))
				#person.today_schedule = dict.fromkeys(todays_timestamps, self.sectors['Healthcare'].Units_list[building_id][unit_id])
				#for r in range(24):
				#    if person.Campus.sectors['Healthcare'].Units_list[building_id][unit_id].visiting.get(r, -1) == -1:
				#        person.Campus.sectors['Healthcare'].Units_list[building_id][unit_id].visiting[r] = []
				#    person.Campus.sectors['Healthcare'].Units_list[building_id][unit_id].visiting[r].append(person.ID)
				#for t in person.timetable[time.strftime("%A",time.localtime(timestamp)).casefold()]:
				#    if type(person.timetable[time.strftime("%A",time.localtime(timestamp)).casefold()][t]) == dict:
				#        continue
					# print(person.timetable[time.strftime("%A",time.localtime(timestamp)).casefold()][t].Sector, person.ID, person.Status, person.State, time.strftime("%A",time.localtime(timestamp)).casefold(), t)
					# print(person.timetable[time.strftime("%A", time.localtime(timestamp)).casefold()][t].visiting[t])
					# print(person.timetable[time.strftime("%A",time.localtime(timestamp)).casefold()][t].default_visiting[time.strftime("%A",time.localtime(timestamp)).casefold()][t])
					# print(person.timetable[time.strftime("%A",time.localtime(timestamp)).casefold()][t].Building)
					#person.timetable[time.strftime("%A",time.localtime(timestamp)).casefold()][t].visiting[t].remove(person.ID)

				# if self.sectors['Healthcare'].Units_list[building_id][unit_id].visiting.get(temp,None) is None:
				#     self.sectors['Healthcare'].Units_list[building_id][unit_id].visiting[time.localtime(temp)] = [person.ID]
				# else:
				#     self.sectors['Healthcare'].Units_list[building_id][unit_id].visiting[time.localtime(temp)].append(person.ID)

				# for j in range(24):
				#     temp = timestamp + j*60*60
				#     building_id = person.Campus.sectors['Healthcare'].building_ids[0]
				#     unit_id = random.choice(list(person.Campus.sectors['Healthcare'].Units_list[building_id].keys()))
				#     newschedule[time.localtime(temp)] = person.Campus.sectors['Healthcare'].Units_list[building_id][unit_id]
				#     if person.Campus.sectors['Healthcare'].Units_list[building_id][unit_id].visiting.get(time.localtime(temp),None) is None:
				#         person.Campus.sectors['Healthcare'].Units_list[building_id][unit_id].visiting[time.localtime(temp)] = [person.ID]
				#     else:
				#         person.Campus.sectors['Healthcare'].Units_list[building_id][unit_id].visiting[time.localtime(temp)].append(person.ID)
			# else:
			#     #
		temp = self.visitors.copy()
		for v in temp:
			if v.num_of_visited_days > v.num_of_visiting_days:
				self.visitors.remove(v)
				del v
				continue
			else:
				v.num_of_visited_days += 1
			for t in range(8,17):
				v.today_schedule[t] = random.choice(list(v.visiting_dict.keys()))

		for sector in self.sectors:
			#if self.Lockdown > 0:
			#    break
			if self.sectors[sector].Shutdown == 0:
				continue
			self.__sector_shutdown__(sector)

		for building_id in self.buildings:
			if self.buildings[building_id].Shutdown == 1:
				self.__building_shutdown__(building_id)

	@func_timer
	def __save_today_movements_snapshots__(self,day_interval):
		if self.TODAY%day_interval != 0:
			return
		with open(os.path.join(self.SAVEDIR, 'locations.csv'), 'a', newline='') as csv_file:
			csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames4)
			for i in range(24):
				if i % self.pm.result_resolution != 0:
					continue
				for s in self.all_people:
					info = {"day": self.TODAY, "hour": i, "id": s.ID, "x": s.today_schedule[i].location.x, "y": s.today_schedule[i].location.y, "state": s.State, "role": s.Role, "is_atRisk": str(s.is_atRisk), "vaccination_state": s.Vaccination_State}

					csv_writer.writerow(info)

	@func_timer
	def update_contact_window(self):
		'''
		Function updates contact_window of all people with the current day's interactions
		'''
		for person in self.all_people:
			if person.contact_window.full():
				person.contact_window.get()
			contacts, edgeweights = self.__get_contacts__(person)
			temp = []
			for i in range(len(contacts)):
				temp.append((contacts[i],edgeweights[i]))
			person.contact_window.put(temp)

	def plot_positive_cases(self):
		x = [i for i in range(1,self.SIM_DAYS+1)]
		y = [len(i) for i in self.PositivePlaceholder]
		# plt.xlabel("day")
		# plt.ylabel("positive_cases")
		plt.title("positive_graph")
		plt.plot(x, y, label="positive_cases")
		plt.plot(x,self.Cumulative_Infections, label="Cumulative_Infections")
		plt.plot(x,self.DailyInfections, label='NewInfections')
		z = [sum(y[:i+1]) for i in range(len(y))]
		plt.plot(x,z, label="cumulative_positive_cases")
		plt.legend(loc='upper left')
		plt.show()

	@func_timer
	def __risk_assigning__(self):
		threshold = 150
		count = 0
		for i in self.AFreeP+self.AQuarantinedP+self.SFreeP+self.SHospitalizedP+self.SIsolatedP+self.SIcuP:
			for j in self.all_people:
				if j.is_atRisk:
					continue
				if  self.attribute_matrix[i.ID][j.ID] > 0:
					j.risk += self.attribute_matrix[i.ID][j.ID]
					# print(j.risk)
				if j.risk > threshold:
					j.is_atRisk = True
					count += 1
		# print("------------------------------------------------------------Number of contacts traced are: ",count)

	def __set_risk_to_zero__(self):
		for i in self.all_people:
			i.risk = 0
			i.is_atRisk = False


	def __update_visitors__(self):
		num_infect_visitors = round(np.random.normal(self.pm.Daily_Visitors*self.pm.outside_infection_prob,self.pm.Daily_Visitors*self.pm.outside_infection_prob/3))
		for i in range(max(num_infect_visitors,0)):
			new_visitor = visitor(Campus=self,ID=len(self.all_people)+len(self.visitors)+1,num_of_visiting_days=max(round(np.random.normal(self.pm.avg_visiting_days, self.pm.avg_visiting_days/3)),1))
			new_visitor.State = new_visitor.states[1]   # changing state to asymptomatic
			self.visitors.append(new_visitor)

	def infect_outsiders(self):
		num_infected = np.random.binomial(len(self.Workers)+sum([1 for _ in self.Profs if _.residence_unit.Id == -1]),self.pm.outside_infection_prob)
		for person in random.sample(self.Workers,num_infected):
			self.__infect_person__(person)
