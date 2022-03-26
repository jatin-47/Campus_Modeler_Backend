import os
import json
import time
import ctypes
import random
import numpy as np

from shapely.geometry import Point
import pandas as pd
import json
import csv
from queue import Queue

from .statemachine import AgentStateA, VaccinationStatus
from .responses_generator_code import generate_record
from .responses_generator_code2 import generate_record2
from .graph_utils import CG_pm


class person(AgentStateA, VaccinationStatus):
	""" Class for describing students

	Args:
		Campus              : Object of Campus Class
		ID                  : Id of the person
		dept                : Departemnt the person belongs(only for student,profs)
		inCampus            : is True when the person is inCampus
		age                 : age of the person
		ageclass            : the ageclass type which the person belongs
		role                : role of the person like student, prof or staff
		year                : year of the student(only for student)
		schedule            : schedule of the person
		residence           : Residence building of the person
	"""


	def __init__(self, Campus=None,risk=0, ID=0, dept=None, inCampus=True, age=-1, ageclass=-1, role=None, year=None, schedule=None, residence=None, Comorbidty_matrix=None):
		super(person,self).__init__()
		self.ID             = ID
		self.Age            = age
		self.AgeClass       = ageclass
		self.residence      = residence
		self.Campus         = Campus
		self.inCampus       = inCampus
		self.Role           = role
		self.dept           = dept
		self.today_schedule = {}
		self.in_hospital	= False
		self.year           = year

		self.re_test        = 0
		self.Family_list_obj = []


		self.timetable      = {"sunday": {}, "monday": {}, "tuesday": {}, "wednesday": {}, "thursday": {}, "friday": {}, "saturday": {}}

		self.Disease 		= []
		self.risk = risk
		self.is_atRisk = False

		self.Isolation_Days = 0
		self.Q_building = -1
		self.Q_unit = -1

		if Comorbidty_matrix!=None:
			self.__get_disease__(Comorbidty_matrix)

		self.update_objects(self.Campus)

		self.final_times = {'monday':[],'tuesday':[],'wednesday':[],'thursday':[],'friday':[], 'saturday':[], 'sunday':[]}


		self.contact_window = Queue(maxsize=CG_pm.duration)
		# self.contact_window = [] #will contain all people from he could spread virus to if is infected for the last few days #TODO: make it a proper queue/sliding_window

	def about(self):
		print("Person id: {},Person Role {}, Person State: {}, Person Status: {}, Person TestingState: {}".format(self.ID,self.Role, self.State, self.Status, self.state))

	def get_schedule(self):
		pass

	def get_prob_severity(self,ProbSeverity):
		for i in self.Disease:
			ProbSeverity = ProbSeverity
		return ProbSeverity

	def __get_disease__(self, CM):
		for i in CM.items(): #Cm is comorbidity matrix
			probablity = [i[1][self.AgeClass],1-i[1][self.AgeClass]]
			has_disease = random.choices([True, False],weights=probablity)[0]
			if has_disease:
				self.Disease.append(i[0])

	def get_death_rate(self,deafaultDR):
		for i in self.Disease:
			deafaultDR = deafaultDR
		return deafaultDR

	def get_timetable_from_courses_list(self):
		"""
		This function creates the timetable from the courses list
		"""

		for subject in self.courses_list:

			if self.Campus.pm.courses_time_location.get(subject, None) is None:
				continue
			if self.Campus.pm.courses_time_location[subject]['room'] is None:
				class_room = None
			else:
				class_room = random.choice(self.Campus.pm.courses_time_location[subject]['room'].split(","))
			if class_room not in self.Campus.SpecialRooms:
				continue
			timings = self.Campus.pm.courses_time_location[subject]['timings']
			#print(slot_name)
			try:
				for classes, times in timings.items():
					self.timetable[times[0]][int(times[1].split('-')[0])] = self.Campus.SpecialRooms[class_room]
					self.Campus.SpecialRooms[class_room].isclassroom = True
			except:
				assert False

	def get_movements_from_survey_info(self):
		"""
		This function is used for generating movwments from the survey information
		"""
		record = generate_record2(self.Role[0].upper()+self.Role[1:])
		# print(record)

		# giving working hours to faculty and staff during weekdays
		self.working_hours_weekdays = []
		temp_times = list(record[0][1].keys())
		wts = np.array(list(record[0][1].values()))
		wts=wts/np.sum(wts)
		temp_working_hours = np.random.choice(temp_times,size=record[0][0],replace=False,p=wts)
		# print(temp_working_hours)
		if temp_working_hours[0] != 'None':
			for i in temp_working_hours:
				times = i.split('-')
				time1 = int(times[0][:-2])
				time2 = int(times[1][:-2])
				if times[0][-2:] == 'pm':
					time1 = int(times[0][:-2])+12
				if times[1][-2:] == 'pm':
					time2 = int(times[1][:-2])+12
				# print(time1,time2)
				self.working_hours_weekdays.extend(list(range(time1,time2)))
		# print(self.working_hours_weekdays)

		# giving working hours to faculty and staff during weekends
		self.working_hours_weekends = []
		temp_times = list(record[1][1].keys())
		wts = np.array(list(record[1][1].values()))
		wts=wts/np.sum(wts)
		temp_working_hours = np.random.choice(temp_times,replace=False,size=record[1][0],p=wts)
		# print(temp_working_hours)
		if temp_working_hours[0] != 'None':
			for i in temp_working_hours:
				times = i.split('-')
				time1 = int(times[0][:-2])
				time2 = int(times[1][:-2])
				if times[0][-2:] == 'pm':
					time1 = int(times[0][:-2])+12
				if times[1][-2:] == 'pm':
					time2 = int(times[1][:-2])+12
				# print(time1,time2)
				self.working_hours_weekends.extend(list(range(time1,time2)))

		for day in self.timetable:
			if day in ["saturday","sunday"]:
				for t in self.working_hours_weekends:
					if self.timetable[day][t] == self.residence_unit:
						try:
							self.timetable[day][t] = self.office_unit
						except:
							self.timetable[day][t] = self.workplace_unit
			else:
				for t in self.working_hours_weekdays:
					if self.timetable[day][t] == self.residence_unit:
						try:
							self.timetable[day][t] = self.office_unit
						except:
							self.timetable[day][t] = self.workplace_unit

		#mapping places in survey to their ids
		with open('data_IITJ/survey_data/building_name_to_id_mapping.csv', 'r',encoding="utf8") as file:
			reader1 = csv.reader(file)
			building_name_to_id = {}
			dum = 0
			for row in reader1:
				if dum == 0:
					dum+=1
					continue
				building_name_to_id[row[0]] = int(row[1])

		#selecting places of visit
		no_of_places = record[2][0]

		temp_response_keys = list(record[2][1].keys())
		for i in temp_response_keys:
			if i == "Student's Hostel":
				continue
			if i == "Type B- park":
				continue
			if building_name_to_id[i] == -1:
				record[2][1].pop(i)
				continue
		places_of_visit= record[2][1]
		# print(places_of_visit)

		no_of_times_eat_out = record[3]
		temp_response_keys = list(record[4].keys())
		for i in temp_response_keys:
			if building_name_to_id[i] == -1:
				record[4].pop(i)
				continue
		eateries= record[4]
		# print(eateries)

		#TODO: Remove the hardcoding
		weekdays = random.sample(['monday','tuesday','wednesday','thursday','friday'], 2) ##selecting 2 weekdays to go out
		next_day = {'monday':'tuesday','tuesday':'wednesday','wednesday':'thursday','thursday':'friday','friday':'saturday'}
		time_day = {'monday':0,'tuesday':24,'wednesday':48,'thursday':72,'friday':96,'saturday':120,'sunday':144}
		list_places = {}
		for day in weekdays:
			if no_of_places == 0:
				break
			places = random.choices(list(places_of_visit.keys()),list(places_of_visit.values()),k=no_of_places)    # think of taking sq root of wts
			list_places[day] = {i:places_of_visit[i] for i in places}


		self.final_times['saturday'] = random.choices([i for i in range(6,24) if i not in self.working_hours_weekends],k=2) # assuming they spend 2 hrs outside
		self.final_times['sunday'] = random.choices([i for i in range(6,24) if i not in self.working_hours_weekends],k=2) # assuming they spend 2 hrs outside


		lib_times_eateries=[]
		count_outside_hours = 0
		for day in weekdays:
			last_working_time = 22
			while self.timetable[day][last_working_time] == self.residence_unit and last_working_time > 14:
				last_working_time-=1
			sleep_time = 22 # assuming sleep time is 10pm
			no_of_hours_weekdays = 2 # assuming they spend 2 hours outside
			outside_hours = random.sample(list(range(last_working_time+1,sleep_time)), min(len(range(last_working_time+1,sleep_time)),no_of_hours_weekdays))
			count_outside_hours += 1
			for hour in outside_hours:
				if hour <= 23:
					self.final_times[day].append(hour)
					lib_times_eateries.append(hour+time_day[day])
				else:
					self.final_times[next_day[day]].append(hour-24)
					lib_times_eateries.append(hour+time_day[day])

		no_weekends_eateries=0
		if no_of_times_eat_out!=0:
			no_weekends_eateries  =  random.sample(list(range(1,min([2,no_of_times_eat_out])+1)),1)[0]

		no_weekdays_eateries = min(no_of_times_eat_out - no_weekends_eateries, count_outside_hours)
		# print(len(lib_times_eateries),no_weekdays_eateries)
		try:
			dist_eateries_weekdays = random.sample(lib_times_eateries,no_weekdays_eateries)
		except:
			dist_eateries_weekdays = []

		for day in weekdays:
			for hour in self.final_times[day]:
				k={}
				if hour+time_day[day] not in dist_eateries_weekdays:
					if list_places == {}:
						continue
					# for building in list_places[day]:
					# 	k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekdays'][str(building)] + year_wise_placeweights[str(self.year)]['weekdays'][str(building)]
					# self.timetable[day][hour] = k
					# print(day,list_places)
					self.timetable[day][hour] = list_places[day]
				else:
					# for building in eateries:
					# 	k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekdays'][str(building)] + year_wise_placeweights[str(self.year)]['weekdays'][str(building)]
					self.timetable[day][hour] = eateries

		lib_times_eateries=[]
		for times in self.final_times['saturday']:
			lib_times_eateries.append(time_day['saturday']+times)
		for times in self.final_times['sunday']:
			lib_times_eateries.append(time_day['sunday']+times)


		dist_eateries_weekends = random.sample(list(lib_times_eateries),no_weekends_eateries)

		for times in self.final_times['saturday']:
			# k={}
			if times not in dist_eateries_weekends:
				# for building in weekend_places_of_visit:
				# 	k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekends'][str(building)] + year_wise_placeweights[str(self.year)]['weekends'][str(building)]
				# self.timetable['saturday'][times] = k
				self.timetable['saturday'][times] = places_of_visit
			else:
				# for building in eateries:
				# 	k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekends'][str(building)] + year_wise_placeweights[str(self.year)]['weekends'][str(building)]
				self.timetable['saturday'][times] = eateries
			# k={}
		for times in self.final_times['sunday']:
			if times not in dist_eateries_weekends:
				# for building in weekend_places_of_visit:
				# 	k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekends'][str(building)] + year_wise_placeweights[str(self.year)]['weekends'][str(building)]
				self.timetable['sunday'][times] = places_of_visit
			else:
				# for building in eateries:
				# 	k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekends'][str(building)] + year_wise_placeweights[str(self.year)]['weekends'][str(building)]
				self.timetable['sunday'][times] = eateries

		# to avoid empty dictionary and find final_times
		self.final_times = {"monday": [], "tuesday": [], "wednesday": [], "thursday": [], "friday": [], "saturday": [], "sunday": []}
		for day in self.timetable:
			for i in range(24):
				if type(self.timetable[day][i]) == dict and len(self.timetable[day][i]) == 0:
					self.timetable[day][i] = self.residence_unit
					# print("it is zero here", day, i, self.personID)
				if type(self.timetable[day][i]) == dict:
					self.final_times[day].append(i)
					self.timetable[day][i] = {(key if key in ["Student's Hostel","Type B- park"] else building_name_to_id[key]):(value) for key, value in self.timetable[day][i].items() }
					# print(self.ID,day,i,self.timetable[day][i])



		# assert 1==0
	def send_person_to_workplace(self, workplace, days=("monday","tuesday","wednesday","thursday","friday"), time_frames=(8,9,10,11,12,2,3,4,5)):
		"""
		Updates person's timetable attribute for his working hours in workplace
		:param workplace: The workplace unit object.
		:param days: List of days in which the person goes to his workplace (eg. ["monday","tuesday"])
		:param time_frames: List of times at which the person will be in his workplace (eg. [8,9,10,11,12,2,3,4,5])
		:return: None
		"""
		for day in days:
			for i in time_frames:
				if 8 <= i <= 17 and i != 13:
					self.timetable[day][i] = workplace


class student(person):
	"""
	Class for describing students

	Args:
		Campus              : Object of Campus Class
		ID                  : Id of the person
		dept                : Departemnt the student belongs
		inCampus            : is True when the person is inCampus
		age                 : age of the person
		ageclass            : the ageclass type which the person belongs
		role                : role of the person (here "student")
		courses_list        : list of courses of the student
		year                : year of the student
		prog                : program the student is enrolled like UG or PG
		schedule            : schedule of the person
		residence           : Residence building of the person
		personal_choice     : survey data_IITKGP choices
		batch               : batch of the student like 18ME,19CS etc.
		mess                : mess of the student
	"""
	def __init__(self,  Campus=None, ID=0, dept=None, inCampus=True, age=-1, ageclass=-1, role="student",courses_list = None, year=None, prog=None, schedule=None, residence=None, personal_choice=None, batch = None,mess_building_id = None, mess_no = None, lab_code = None):
		super().__init__(ID=ID, role=role, age=age, ageclass=ageclass, dept=dept, residence=residence, inCampus=inCampus)

		self.Campus = Campus
		self.schedule = schedule
		self.courses_list = courses_list
		self.year = year
		self.prog = prog
		self.residence_building_id = int(self.residence[0])
		self.residence_unit  = self.Campus.Units_Placeholder[self.residence_building_id][self.residence[1]+self.Campus.Index_Holder[self.residence_building_id]]
		self.residence_point = self.residence_unit.location
		self.personal_choice = personal_choice
		self.batch = batch
		self.lab_code = lab_code
		if mess_no is None:
			self.mess_unit = random.sample(list(self.Campus.sectors['Mess'].Units_list[mess_building_id].values()), k=1)[0]
		else:
			k=[]
			for i in self.Campus.sectors['Mess'].Units_list:
				for j in self.Campus.sectors['Mess'].Units_list[i]:
					k.append(j)

			self.mess_unit = self.Campus.sectors['Mess'].Units_list[i][k[mess_no]]
		for day in self.timetable:
			for i in range(24):
				self.timetable[day][i]=self.residence_unit

		self.get_timetable_from_courses_list()
		# self.get_outside_class_hour_movement()
		if lab_code != None	:
			self.get_lab_timetable()
		# mess movements
		self.give_mess_movements()

	def get_lab_timetable(self):

		for day in self.timetable:
			for k in [8,9,10,11,12,2,3,4]:
				self.timetable[day][k] = self.Campus.SpecialRooms[self.lab_code]


	def get_timetable(self):
		"""
		Generates timetable from the schedule
		"""
		# print("entered get_timetable")
		#for day in self.timetable:
		#	for i in range(24):
				#self.timetable[day][str(i)+'-'+str(i+1)]=self.Campus.ParamObj.building_name[self.residence_unit.Building]
				#self.timetable[day][i]=self.residence_unit
				# if i >= 18 or i < 8:
				# 	weights = []
				# 	for key in wifidata:
				# 		weights.append(wifidata[key][day][str(i)+'-'+str(i+1)])
				# 	building_id = random.choices([i for i in range(self.Campus.Total_Num_Buildings)],weights)[0]
				# 	unit_id = random.choice(list(self.Campus.Units_Placeholder[building_id].keys()))
				# 	self.timetable[day][i] = self.Campus.Units_Placeholder[building_id][unit_id]

		for subject in self.schedule:
			class_room=self.schedule[subject]['room']
			slot_name=self.schedule[subject]['slot']
			#print(slot_name)
			for classes,times in slots[slot_name].items():
				#print(times[0]+' '+times[1])
				if len(slot_name)>3:
					timing=times[1].split('-')
					starting=int(timing[0])
					ending=int(timing[-1])
					for i in range(starting, ending):
						try:
							self.timetable[times[0]][i]=self.Campus.__room2unit__(class_room)
							self.Campus.__room2unit__(class_room).isclassroom = True
						except:
							altroom = sum([ord(char) for char in class_room])+self.Campus.Index_Holder[42]
							self.timetable[times[0]][i]=self.Campus.Units_Placeholder[42][altroom]
							self.Campus.Units_Placeholder[42][altroom].isclassroom = True
				else:
					self.timetable[times[0]][int(times[1].split('-')[0])]=self.Campus.__room2unit__(class_room)
					self.Campus.__room2unit__(class_room).isclassroom = True

		# movement outside class hours
		with open('data_IITKGP/survey_data/building_name_to_id_mapping.csv', 'r',encoding="utf8") as file:
			reader1 = csv.reader(file)
			building_name_to_id = {}
			building_id_to_name={}
			for row in reader1:
				building_name_to_id[row[0]] = int(row[1])
				building_id_to_name[int(row[1])] =row[0]





		l = len(responses[building_id_to_name[self.residence_building_id]][str(self.year)])
		if l == 0:
			return
		response_no = responses[building_id_to_name[self.residence_building_id]][str(self.year)][self.personal_choice%l]
		df_req = surveydata[surveydata["Unnamed: 0"] == response_no]
		#self.clustering has to be done
		no_of_weekdays = df_req.iloc[0,4]
		no_of_hours_weekdays = df_req.iloc[0,5]

		places_of_visit = []
		for i in df_req.iloc[0,6].split(";"):
			if i == 'Other Hall of Residence':
				places_of_visit.append('Other Hall of Residence')
				continue
			elif i == 'A Department':
				places_of_visit.append('A Department')
				continue
			elif i == 'Nalanda':
				continue
			elif building_name_to_id[i] == -1:
				continue
			places_of_visit.append(building_name_to_id[i])

		no_of_diff_places = df_req.iloc[0,7]

		sleep_time = df_req.iloc[0,12]
		if sleep_time == 'I usually stay in my room':
			sleep_time = 21
		else:
			sleep_time = int(sleep_time.split('-')[1][:-2])
			if sleep_time < 4:
				sleep_time += 24
			else:
				sleep_time+=12

		if df_req.iloc[0,10] != "Never": temp_times = list(map(lambda x: x.split("-"),df_req.iloc[0,10].split(";")))
		else: temp_times = None
		weekend_times = []
		# print(temp_times)
		if temp_times != None:
			for time_range in temp_times:
				if time_range[0] == 'Never':
					continue
				if time_range[0][-2:] == "PM":
					weekend_times.extend([int(time_range[0][:-2])+12,int(time_range[0][:-2])+1+12])
				else:
					weekend_times.extend([int(time_range[0][:-2]),int(time_range[0][:-2])+1])

		no_times_eateries = df_req.iloc[0,8]

		eateries = []
		for i in df_req.iloc[0,9].split(";"):
			if building_name_to_id[i] == -1:
				continue
			eateries.append(building_name_to_id[i])


		weekend_places_of_visit = []
		for i in df_req.iloc[0,11].split(";"):
			if building_name_to_id[i] == -1:
				continue
			elif building_name_to_id[i] == 'Nalanda':
				continue
			weekend_places_of_visit.append(building_name_to_id[i])


		days = random.sample(['monday','tuesday','wednesday','thursday','friday'],no_of_weekdays)
		next_day = {'monday':'tuesday','tuesday':'wednesday','wednesday':'thursday','thursday':'friday','friday':'saturday'}
		time_day = {'monday':0,'tuesday':24,'wednesday':48,'thursday':72,'friday':96}
		list_places = {}
		m = 0
		for day in days:
			if len(places_of_visit) == 0:
				break
			if no_of_diff_places == 0:
				break
			list_places[day] = places_of_visit[m:m+no_of_diff_places]
			while len(list_places[day])<no_of_diff_places:
				list_places[day].extend(places_of_visit[0:no_of_diff_places-len(list_places[day])])
				m = -len(list_places[day])
				# print("hi", len(list_places[day]),no_of_diff_places)
			m+=no_of_diff_places
			if(m>no_of_diff_places):
				m = m % no_of_diff_places





		self.final_times['saturday'] = weekend_times
		self.final_times['sunday'] = weekend_times




		lib_times_eateries=[]
		count_outside_hours = 0
		for day in days:
			last_class_time = 17
			while self.timetable[day][last_class_time] == self.timetable[day][18] and last_class_time > 14:
				last_class_time-=1

			outside_hours = random.sample(list(range(last_class_time+1,sleep_time)), min(len(range(last_class_time+1,sleep_time)),no_of_hours_weekdays))
			count_outside_hours += 1
			for hour in outside_hours:
				if hour <= 23:
					self.final_times[day].append(hour)
					lib_times_eateries.append(hour+time_day[day])
				else:
					self.final_times[next_day[day]].append(hour-24)
					lib_times_eateries.append(hour+time_day[day])

		no_weekends_eateries=0
		if len(weekend_times)!=0 and no_times_eateries!=0:
			no_weekends_eateries  =  random.sample(list(range(1,min([len(weekend_times),3,no_times_eateries])+1)),1)[0]

		no_weekdays_eateries = min(no_times_eateries - no_weekends_eateries, count_outside_hours)
		# print(len(lib_times_eateries),no_weekdays_eateries)
		try:
			dist_eateries_weekdays = random.sample(lib_times_eateries,no_weekdays_eateries)
		except:
			dist_eateries_weekdays = []

		for day in days:
			for hour in self.final_times[day]:
				k={}
				if hour+time_day[day] not in dist_eateries_weekdays:
					if len(list_places) == 0:
						continue
					for building in list_places[day]:
						k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekdays'][str(building)] + year_wise_placeweights[str(self.year)]['weekdays'][str(building)]
					self.timetable[day][hour] = k
				else:
					for building in eateries:
						k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekdays'][str(building)] + year_wise_placeweights[str(self.year)]['weekdays'][str(building)]
					self.timetable[day][hour] = k

		lib_times_eateries=[]
		for times in weekend_times:
			lib_times_eateries.append(times)
			lib_times_eateries.append(times+24)


		dist_eateries_weekends = random.sample(list(lib_times_eateries),no_weekends_eateries)

		for times in weekend_times:
			k={}
			if times not in dist_eateries_weekends:
				for building in weekend_places_of_visit:
					k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekends'][str(building)] + year_wise_placeweights[str(self.year)]['weekends'][str(building)]
				self.timetable['saturday'][times] = k
			else:
				for building in eateries:
					k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekends'][str(building)] + year_wise_placeweights[str(self.year)]['weekends'][str(building)]
				self.timetable['saturday'][times] = k
			k={}
			if times+24 not in dist_eateries_weekends:
				for building in weekend_places_of_visit:
					k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekends'][str(building)] + year_wise_placeweights[str(self.year)]['weekends'][str(building)]
				self.timetable['sunday'][times] = k
			else:
				for building in eateries:
					k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekends'][str(building)] + year_wise_placeweights[str(self.year)]['weekends'][str(building)]
				self.timetable['sunday'][times] = k

		# to avoid empty dictionary and find final_times
		self.final_times = {"monday": [], "tuesday": [], "wednesday": [], "thursday": [], "friday": [], "saturday": [], "sunday": []}
		for day in self.timetable:
			for i in range(24):
				if type(self.timetable[day][i]) == dict and len(self.timetable[day][i]) == 0:
					self.timetable[day][i] = self.residence_unit
					# print("it is zero here", day, i, self.personID)
				if type(self.timetable[day][i]) == dict:
					self.final_times[day].append(i)




	def get_outside_class_hour_movement(self):
		"""
		This is used for generation of movements outside class hours
		"""
		if self.dept == "BS" or self.dept == "BL":
			self.dept = "BB"
		elif self.dept == "CS" or self.dept == "AI":
			self.dept = "CSE"
		elif self.dept == "CHM":
			self.dept = "CY"
		elif self.dept == "HS":
			self.dept = "HSS"
		elif self.dept == "EN" or self.dept == "SS" or self.dept == "VSS" or self.dept == "" or self.dept == "PP" or self.dept == "DCS" or self.dept == "COE" or self.dept == "CPS" or self.dept == "DE" or self.dept == "MFE"  or self.dept == "SIOT" or self.dept == "TFE" or self.dept == "AMD":
			self.dept = random.choice(["-","IDRP -DH", "IDRP", "IDRP-MMT", "IDRP SOI"])

		if self.prog == "B" or self.prog == "M" or self.prog == "MT":
			temp_prog = "UG"
		else:
			temp_prog = "PG"

		if self.year == 1:
			temp_year = "1 st"
		elif self.year == 2:
			temp_year = "2 nd"
		elif self.year == 3:
			temp_year = "3 rd"
		elif self.year == 4:
			temp_year = "4 th"
		else:
			temp_year = "5 th"

		response = generate_record([self.dept, self.residence_building_id, temp_prog, temp_year])

		with open('data_IITJ/survey_data/building_name_to_id_mapping.csv', 'r',encoding="utf8") as file:
			reader1 = csv.reader(file)
			building_name_to_id = {}
			dum = 0
			for row in reader1:
				if dum == 0:
					dum+=1
					continue
				building_name_to_id[row[0]] = int(row[1])



		self.final_times = {'monday':[],'tuesday':[],'wednesday':[],'thursday':[],'friday':[], 'saturday':[], 'sunday':[]}

		#self.clustering has to be done
		no_of_weekdays = response[2]
		no_of_hours_weekdays = response[3]
		no_of_diff_places = response[5]


		temp_response_keys = list(response[4].keys())
		for i in temp_response_keys:
			if i == "A Department":
				response[4].pop(i)
				continue
			if building_name_to_id[i] == -1:
				response[4].pop(i)
				continue
		places_of_visit= response[4]

		sleep_time = response[10]
		if sleep_time == 'I usually stay in my room':
			sleep_time = 21
		else:
			sleep_time = int(sleep_time.split('-')[1][:-2])
			if sleep_time < 4:
				sleep_time += 24
			else:
				sleep_time+=12
		wts = np.array(list(response[8][1].values()))
		wts=wts/np.sum(wts)
		temp_times = np.random.choice(list(response[8][1].keys()),response[8][0],p=wts,replace=False)
		weekend_times = []
		if temp_times[0] != "Never":
			for time_range in temp_times:
				temp_time_range = time_range.split("-")
				if temp_time_range[0][-2:] == "PM":
					weekend_times.extend([int(temp_time_range[0][:-2])+12,int(temp_time_range[0][:-2])+1+12])
				else:
					weekend_times.extend([int(temp_time_range[0][:-2]),int(temp_time_range[0][:-2])+1])


		no_times_eateries = response[6]


		temp_response_keys = list(response[7].keys())
		for i in temp_response_keys:
			if building_name_to_id[i] == -1:
				response[7].pop(i)
				continue
		eateries=response[7]



		temp_response_keys = list(response[9].keys())
		for i in temp_response_keys:
			if building_name_to_id[i] == -1:
				response[9].pop(i)
				continue
		weekend_places_of_visit=response[9]

		days = random.sample(['monday','tuesday','wednesday','thursday','friday'],no_of_weekdays)
		next_day = {'monday':'tuesday','tuesday':'wednesday','wednesday':'thursday','thursday':'friday','friday':'saturday'}
		time_day = {'monday':0,'tuesday':24,'wednesday':48,'thursday':72,'friday':96}
		list_places = {}
		for day in days:
			if no_of_diff_places == 0:
				break
			places = random.choices(list(places_of_visit.keys()),list(places_of_visit.values()),k=no_of_diff_places)    # think of taking sq root of wts
			list_places[day] = {i:places_of_visit[i] for i in places}





		self.final_times['saturday'] = weekend_times
		self.final_times['sunday'] = weekend_times




		lib_times_eateries=[]
		count_outside_hours = 0
		for day in days:
			last_class_time = 17
			while self.timetable[day][last_class_time] == self.timetable[day][18] and last_class_time > 14:
				last_class_time-=1

			outside_hours = random.sample(list(range(last_class_time+1,sleep_time)), min(len(range(last_class_time+1,sleep_time)),no_of_hours_weekdays))
			count_outside_hours += 1
			for hour in outside_hours:
				if hour <= 23:
					self.final_times[day].append(hour)
					lib_times_eateries.append(hour+time_day[day])
				else:
					self.final_times[next_day[day]].append(hour-24)
					lib_times_eateries.append(hour+time_day[day])

		no_weekends_eateries=0
		if len(weekend_times)!=0 and no_times_eateries!=0:
			no_weekends_eateries  =  random.sample(list(range(1,min([len(weekend_times),3,no_times_eateries])+1)),1)[0]

		no_weekdays_eateries = min(no_times_eateries - no_weekends_eateries, count_outside_hours)
		# print(len(lib_times_eateries),no_weekdays_eateries)
		try:
			dist_eateries_weekdays = random.sample(lib_times_eateries,no_weekdays_eateries)
		except:
			dist_eateries_weekdays = []

		for day in days:
			for hour in self.final_times[day]:
				k={}
				if hour+time_day[day] not in dist_eateries_weekdays:
					if list_places == {}:
						continue
					# for building in list_places[day]:
					# 	k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekdays'][str(building)] + year_wise_placeweights[str(self.year)]['weekdays'][str(building)]
					# self.timetable[day][hour] = k
					# print(day,list_places)
					self.timetable[day][hour] = list_places[day]
				else:
					# for building in eateries:
					# 	k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekdays'][str(building)] + year_wise_placeweights[str(self.year)]['weekdays'][str(building)]
					self.timetable[day][hour] = eateries

		lib_times_eateries=[]
		for times in weekend_times:
			lib_times_eateries.append(times)
			lib_times_eateries.append(times+24)


		dist_eateries_weekends = random.sample(list(lib_times_eateries),no_weekends_eateries)

		for times in weekend_times:
			# k={}
			if times not in dist_eateries_weekends:
				# for building in weekend_places_of_visit:
				# 	k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekends'][str(building)] + year_wise_placeweights[str(self.year)]['weekends'][str(building)]
				# self.timetable['saturday'][times] = k
				self.timetable['saturday'][times] = weekend_places_of_visit
			else:
				# for building in eateries:
				# 	k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekends'][str(building)] + year_wise_placeweights[str(self.year)]['weekends'][str(building)]
				self.timetable['saturday'][times] = eateries
			# k={}
			if times+24 not in dist_eateries_weekends:
				# for building in weekend_places_of_visit:
				# 	k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekends'][str(building)] + year_wise_placeweights[str(self.year)]['weekends'][str(building)]
				self.timetable['sunday'][times] = weekend_places_of_visit
			else:
				# for building in eateries:
				# 	k[building] = hall_wise_placeweights[str(self.residence_building_id)]['weekends'][str(building)] + year_wise_placeweights[str(self.year)]['weekends'][str(building)]
				self.timetable['sunday'][times] = eateries

		# to avoid empty dictionary and find final_times
		self.final_times = {"monday": [], "tuesday": [], "wednesday": [], "thursday": [], "friday": [], "saturday": [], "sunday": []}
		for day in self.timetable:
			for i in range(24):
				if type(self.timetable[day][i]) == dict and len(self.timetable[day][i]) == 0:
					self.timetable[day][i] = self.residence_unit
					# print("it is zero here", day, i, self.personID)
				if type(self.timetable[day][i]) == dict:
					self.final_times[day].append(i)
					self.timetable[day][i] = {(key if key in ["Other Hostel of Residence","A Department"] else building_name_to_id[key]):(value) for key, value in self.timetable[day][i].items() }
					# print(self.timetable[day][i])



	def give_mess_movements(self):
		for day in self.timetable:
			for k in [7,12,16,19]:
				if self.timetable[day][k] == self.residence_unit and self.timetable[day][k+1] == self.residence_unit :
					a = random.choice([0,1])
					self.timetable[day][k+a] = self.mess_unit
				elif self.timetable[day][k] != self.residence_unit and self.timetable[day][k+1] == self.residence_unit :
					self.timetable[day][k+1] = self.mess_unit
				elif self.timetable[day][k] == self.residence_unit and self.timetable[day][k+1] != self.residence_unit :
					self.timetable[day][k] = self.mess_unit



class professor(person):
	"""
	Class for describing professor

	Args:
		lab                         : lab unit if any the professor works in
		office                      : office unit of the professor
		Campus                      : Object of Campus Class
		HouseNo                     : house number of residence of professor
		residence_building_id       : building residence Id
		courses_list                : course which the faculty takes
		ID                          : Id of the person
		dept                        : Department the faculty belongs
		inCampus                    : is True when the person is inCampus
		age                         : age of the person
		ageclass                    : the ageclass type which the person belongs
		role                        : role of the person (here "faculty")
		schedule                    : schedule of the person
	"""
	def __init__(self, prob_to_go_out=0.05, lab=None, office=None, Campus=None, residence_unit_id = None, residence_building_id=None, courses_list=None, ID=0, dept=None, inCampus=True, age=-1, ageclass=-1, role="faculty", schedule=None, adult_family_members = 0, child_family_members = 0):
		super().__init__(ID=ID, role=role, age=age, ageclass=ageclass,dept=dept)
		self.Campus = Campus
		self.courses_list = courses_list
		self.residence = "Faculty Quarters"
		self.residence_building_id = residence_building_id
		self.adult_family_members = adult_family_members
		self.child_family_members = child_family_members
		self.residence_unit = self.Campus.Units_Placeholder[residence_building_id][residence_unit_id]
		self.residence_point = self.residence_unit.location
		self.office_unit = self.residence_unit
		self.prob_to_go_out = prob_to_go_out
		self.office = self.lab = lab
		self.prof_timetable = schedule
		for day in self.timetable:
			for i in range(24):
				self.timetable[day][i]=self.residence_unit
		if self.Campus.pm.CampusName == "IITKGP":
			self.generate_exp_schedule()
		else:
			self.get_timetable_from_courses_list()
			if self.Campus.pm.CampusName == "IITJ":
				self.get_movements_from_survey_info()
			else:
				self.send_person_to_workplace(self.office_unit)


			"""
			for day in self.timetable:
				for i in range(24):
					if i < 8 or i >= 18 or i == 13:
						self.timetable[day][i] = self.residence_unit
						if i >= 18 and i <= 21:
							if random.random()<self.prob_to_go_out:
								building_id = random.choices(self.Campus.sectors['Market'].building_ids, weights=[95,5])[0] #Hard Coded 95 5 weights for market and rabi shop respectively
								unit_id = random.choice(list(self.Campus.sectors['Market'].Units_list[building_id].keys()))
								self.timetable[day][i] = self.Campus.sectors['Market'].Units_list[building_id][unit_id]
						#self.daily_schedule_expected[day][i] = 'residence'+str(self.residence_building_id)
					else:
						if day != 'sunday':
							self.timetable[day][i] = self.office_unit
							gaus_val = np.random.normal(0,1,1)
							if gaus_val >= -1 and gaus_val <=1: self.timetable[day][i] = self.lab_unit
							#self.daily_schedule_expected[day][i] = 'office'+self.office
						else:
							self.timetable[day][i] = self.residence_unit
							if random.random()<self.prob_to_go_out:
								building_id = random.choice(self.Campus.sectors['Market'].building_ids+self.Campus.sectors['Grounds'].building_ids+self.Campus.sectors['Restaurant'].building_ids) #TODO: have to send systematically on sundays; for now he has equal probabilty of going anywhere(i.e. all the mentioned sectors places)
								unit_id = random.choice(list(self.Campus.Units_Placeholder[building_id].keys()))
								self.timetable[day][i] = self.Campus.Units_Placeholder[building_id][unit_id]
							#self.daily_schedule_expected[day][i] = 'residence'+str(self.residence_building_id)

			"""

	def generate_exp_schedule(self):
		"""
		Genrates timetable from the schedule
		"""
		for day in self.timetable:
				for i in range(24):
					if i < 8 or i >= 18 or i == 13:
						self.timetable[day][i] = self.residence_unit
						if i >= 18 and i <= 21:
							if random.random()<self.prob_to_go_out:
								try:
									building_id = random.choices(self.Campus.sectors['Market'].building_ids, weights=[95,5])[0] #Hard Coded 95 5 weights for market and rabi shop respectively
								except:
									building_id = self.Campus.sectors['Market'].building_ids[0]
								unit_id = random.choice(list(self.Campus.sectors['Market'].Units_list[building_id].keys()))
								self.timetable[day][i] = self.Campus.sectors['Market'].Units_list[building_id][unit_id]
						#self.daily_schedule_expected[day][i] = 'residence'+str(self.residence_building_id)
					else:
						if day != 'sunday':
							self.timetable[day][i] = self.office_unit
							gaus_val = np.random.normal(0,1,1)
							if gaus_val >= -1 and gaus_val <=1: self.timetable[day][i] = self.lab_unit
							#self.daily_schedule_expected[day][i] = 'office'+self.office
						else:
							self.timetable[day][i] = self.residence_unit
							if random.random()<self.prob_to_go_out:
								building_id = random.choice(self.Campus.sectors['Market'].building_ids+self.Campus.sectors['Grounds'].building_ids+self.Campus.sectors['Restaurant'].building_ids) #TODO: have to send systematically on sundays; for now he has equal probabilty of going anywhere(i.e. all the mentioned sectors places)
								unit_id = random.choice(list(self.Campus.Units_Placeholder[building_id].keys()))
								self.timetable[day][i] = self.Campus.Units_Placeholder[building_id][unit_id]
							#self.daily_schedule_expected[day][i] = 'residence'+str(self.residence_building_id)

		day = {'0':'monday','1':'tuesday','2':'wednesday','3':'thursday','4':'friday','5':'saturday','6':'sunday'}
		class_start_time = {'0':'8','1':'9','2':'10','3':'11','4':'12','5':'14','6':'15','7':'16','8':'17'}
		try:
			for i in self.prof_timetable:
				for j in i[0]:
					self.prof_timetable[day[j[0]]][class_start_time[j[1]]] = i[1]
		except:
			# Enters this block when the schedule is given as a single subject
			for key, value in self.prof_timetable.items():
				for n in slots[value['slot']]:
					day = slots[value['slot']][n][0]
					times = map(int,slots[value['slot']][n][1].split('-'))
					for start_time in range(*times):
						try:
							#if day == 'wednesday':
							#    if value['room'][0:2] == 'NR' or value['room'][0:2] == 'NC':
							#        print(value['room'])
							#        print(start_time)
							self.timetable[day][start_time] = self.Campus.__room2unit__(value['room'])
							#self.daily_schedule_expected[day][start_time] = key
							#if day == 'wednesday': print(self.daily_schedule_expected['wednesday'])
						except:
							#print(value['room'])
							altroom = sum([ord(char) for char in value['room']])+self.Campus.Index_Holder[42]
							self.timetable[day][start_time]=self.Campus.Units_Placeholder[42][altroom]

class staff(person):
	"""
	Class for describing staff

	Args:
		HouseNo                     : house number of residence of professor
		residence_building_id       : residence building Id
		workplace_buildingid        : Workplace building ID
		Campus                      : Object of Campus Class
		ID                          : Id of the person
		inCampus                    : is True when the person is inCampus
		age                         : age of the person
		ageclass                    : the ageclass type which the person belongs
		role                        : role of the person (here "faculty")
	"""
	def __init__(self,prob_to_go_out=0.1,residence_unit_id=None, residence_building_id=None, workplace_buildingid = None,  Campus=None, ID=0,  inCampus=True, age=-1, ageclass=-1, role="staff", adult_family_members = 0, child_family_members = 0):
		super().__init__(ID=ID, role=role, age=age, ageclass=ageclass,inCampus = inCampus)
		self.Campus = Campus
		self.residence = "Staff Residence"
		self.residence_building_id = residence_building_id
		self.residence_unit = self.Campus.Units_Placeholder[residence_building_id][residence_unit_id]
		self.workplace_buildingid = workplace_buildingid
		self.prob_to_go_out = prob_to_go_out
		self.adult_family_members = adult_family_members
		self.child_family_members = child_family_members
		while True:
			self.workplace_unit_id = random.choice(list(self.Campus.Units_Placeholder[self.workplace_buildingid].keys()))
			self.workplace_unit = self.Campus.Units_Placeholder[self.workplace_buildingid][self.workplace_unit_id]
			if self.workplace_unit.isclassroom:
				continue
			else:
				break
		if self.Campus.pm.CampusName == "IITKGP": self.generate_exp_schedule()
		else:
			for day in self.timetable:
				for i in range(24):
					self.timetable[day][i] = self.residence_unit
			self.get_movements_from_survey_info()

	def generate_exp_schedule(self):
		"""
		Generates timetable for staff
		"""
		for day in self.timetable:
			for i in range(24):
				if i < 8 or i > 18 or i == 13:
					self.timetable[day][i] = self.residence_unit
					if i >= 18 and i <= 21:
						if random.random()<self.prob_to_go_out:
							building_id = random.choices(self.Campus.sectors['Market'].building_ids, weights=[95,5])[0] #Hard coded 95 for Tech Market 5 for Rabi Shop
							unit_id = random.choice(list(self.Campus.sectors['Market'].Units_list[building_id].keys()))
							self.timetable[day][i] = self.Campus.sectors['Market'].Units_list[building_id][unit_id]
						else:
							self.timetable[day][i] = self.residence_unit
				else:
					self.timetable[day][i] = self.workplace_unit

class deskWorker(person):
	"""
	Class for describing workers

	Args :
		Campus                      : Object of Campus Class
		ID                          : Id of the person
		age                         : age of the person
		ageclass                    : the ageclass type which the person belongs
		role                        : role of the person (desk-worker)
		work_building_id            : building id of workplace
		work_building_unit          : workplace unit
	"""
	def __init__(self, Campus = None, ID = 0, age = 1, ageclass = -1, role = "desk_worker",inCampus=True,residence_unit = None, work_building_id = 0, work_building_unit = 0):
		super().__init__(age = age, ID = ID, ageclass = ageclass, role = role, inCampus=inCampus)
		self.Campus = Campus
		self.work_building_id = work_building_id
		self.work_building_unit = work_building_unit
		self.residence_unit = residence_unit
		self.residence_building_id = -1


		self.get_timetable_for_worker()

	def get_timetable_for_worker(self):
		for day in self.timetable:
			for i in range(24):
				if(i>=7 and i<=17):
					self.timetable[day][i] = self.work_building_unit
				else:
					self.timetable[day][i] = self.residence_unit

class nonDeskWorker(person):
	"""
	Class for describing workers

	Args :
		Campus                      : Object of Campus Class
		ID                          : Id of the person
		age                         : age of the person
		ageclass                    : the ageclass type which the person belongs
		role                        : role of the person (desk-worker)
		work_building_id            : building id of workplace
	"""
	def __init__(self, Campus = None, ID = 0, age = 1, ageclass = -1,residence_unit=None, role = "non_desk_worker", work_building_id = 0, inCampus=1):
		super().__init__(age = age, ID = ID, ageclass = ageclass, role = role, inCampus=inCampus)
		self.Campus = Campus
		self.work_building_id = work_building_id
		self.residence_unit = residence_unit
		self.residence_building_id = -1


		self.get_timetable_for_worker()

	def get_timetable_for_worker(self):
		# visit_dict = {}
		# for unit_id in self.Campus.Units_Placeholder[self.work_building_id]:
		# 	visit_dict[self.Campus.Units_Placeholder[self.work_building_id][unit_id]] = 1/len(self.Campus.Units_Placeholder[self.work_building_id])
		for day in self.timetable:
			for i in range(24):
				if (i >= 7 and i <= 17):
					self.timetable[day][i] = {self.work_building_id:1}
					self.final_times[day].append(i)
				else:
					self.timetable[day][i] = self.residence_unit


class visitor(person):
	def __init__(self, Campus=None, ID = 0, age = 1, ageclass = -1, role = "visitor",num_of_visiting_days=1):
		super().__init__(age=age,ID = ID,ageclass = ageclass, role = role,inCampus=False)
		self.Campus = Campus
		self.num_of_visiting_days = num_of_visiting_days
		self.num_of_visited_days = 0
		self.visiting_dict = {}
		self.get_buidlings_for_visitor()
		self.visiting_building_id = random.choice(list(self.visiting_dict.keys()))

	def get_buidlings_for_visitor(self):
		building_dict = {}
		for buiding_id in self.Campus.Units_Placeholder:
			building_dict[buiding_id] = 1
		self.visiting_dict = building_dict



class Family():
	"""
	Class for describing family

	Args:
		person               : object of the person(prof or staff)
		school_id            : Id of school
		adult_family_members : number of adult family members apart from the person
		child_family_members : number of child family members
	"""
	def __init__(self, person, school_id, adult_family_members, child_family_members):
		self.family = []
		self.person = person
		self.fam_id = person.ID
		self.family_residence_building_id = person.residence_building_id
		self.family_residence_unit = person.residence_unit
		self.school_id = school_id
		self.adult_family_members = adult_family_members
		self.child_family_members = child_family_members
		self.__init__family_members()
	def __init__family_members(self):
		"""
		For initialising family members
		"""
		for i in range(self.adult_family_members):
				adult = adult_family_member(Campus= self.person.Campus, ID= self.person.ID + (i+1), inCampus=True, age=-1, ageclass = random.randint(2,5), role="Adult_Family_Member", residence_building_id=self.family_residence_building_id, residence_unit = self.family_residence_unit)
				self.family.append(adult)
		for i in range(self.child_family_members):
				child = child_family_member(Campus=self.person.Campus, ID=self.person.ID + (i+1), inCampus=True, age=-1, ageclass= 1, role="Child_Family_Member", residence_building_id=self.family_residence_building_id, residence_unit = self.family_residence_unit, school_id = self.school_id)
				self.family.append(child)


class child_family_member(person):
	"""
	Class for describing child family member

	Args :
		Campus                      : Object of Campus Class
		ID                          : Id of the person
		inCampus                    : is True when the person is inCampus
		age                         : age of the person
		ageclass                    : the ageclass type which the person belongs
		role                        : role of the person
		residence                   : residence building
		residence_building_unit     : residence unit
		school_id                   : school building id
	"""
	def __init__(self, Campus=None, ID=0, dept=None, inCampus=True, age=-1, ageclass=-1, role=None, residence_building_id=None, residence_unit=None, school_id = 0):
		super().__init__(Campus = Campus, ID = ID, ageclass = ageclass, role = role, age = age)

		self.school_id				= school_id
		self.residence_building_id	= residence_building_id
		self.residence_unit			= residence_unit
		print(self.school_id)
		print(self.Campus.Index_Holder[self.school_id] + random.randint(0,31))
		self.school_unit			= Campus.Units_Placeholder[self.school_id][self.Campus.Index_Holder[self.school_id] + random.randint(0,31)]
		self.get_timetable_child_family_member()

	def get_timetable_child_family_member(self):
		"""
		For timetable of child family member
		"""
		for day in self.timetable:
			for i in range(24):
				if i in range(8, 17):
					self.timetable[day][i]=self.school_unit
				else:
					self.timetable[day][i]=self.residence_unit

class adult_family_member(person):
	"""
	Class for describing adult family member

	Args :
		Campus                      : Object of Campus Class
		ID                          : Id of the person
		inCampus                    : is True when the person is inCampus
		age                         : age of the person
		ageclass                    : the ageclass type which the person belongs
		role                        : role of the person
		residence                   : residence building
		residence_building_unit     : residence unit
	"""
	def __init__(self, Campus=None, ID=0,  inCampus=True, age=-1, ageclass=-1, role=None, residence_building_id=None, residence_unit=None):
		super().__init__(Campus = Campus, ID = ID, ageclass = ageclass, role = role, age = age)
		self.residence_building_id	= residence_building_id
		self.residence_unit			= residence_unit
		self.get_timetable_adult_family_member()

	def get_timetable_adult_family_member(self):
		"""
		For timetable of adult family member
		"""
		for day in self.timetable:
			for i in range(24):
				self.timetable[day][i]=self.residence_unit

'''
def main():
	from .utils import form_schedule
	from .campus import Sector, Unit
	from .parameters import Parameters, slots

	schedule = form_schedule()
	pm = Parameters('shapes/kgpbuildings.shp','Campus_data/KGP Data - Sheet1.csv')
	a = Sector(pm.returnParam())
	p = __init_students__(schedule,a)

	print(p[0].get_timetable())
	for i in range(len(p)):
		start_movement(p[i],p[i].get_timetable(),7)
	for key in p[0].schedule:
		print(time.strftime("%c",key),p[0].schedule[key])

if __name__ == "__main__":
	main()
'''
