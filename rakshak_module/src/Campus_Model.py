import random
import numpy as np
import json
import csv
import copy
from numpy.core.numeric import NaN
import pandas as pd

from .simulate import Simulate
from .calibration import calibrate
from .virusmodel import VirusModel
from .person import student, professor, staff, Family, deskWorker, nonDeskWorker
from .utils import form_schedule, select_courses
from .Campus_Units import Unit, Academic, Residence, Restaurant, Healthcare, Market, Gymkhana, Grounds, Non_Academic, Guest_House, Mess, Buildings





class Campus(Simulate, VirusModel):
	"""
	A Class for storing all the information of the parameters of campus and has functions which is used to initialize them and people and initializes them
	"""

	def __init__(self):

		super().__init__()

		# Timetable Params
		self.Departments 				= self.pm.Departments
		self.Deptwise_Timetable 		= None # dept, year wise timetable

		# Building Parameters
		self.description				= self.pm.description
		self.Number_Units_per_floor     = self.pm.num_rooms_per_floor
		self.Total_Num_Buildings        = len(self.Number_Units_per_floor)
		self.Number_Workers             = self.pm.Number_Workers
		self.Floor                      = self.pm.Floor
		self.Location                   = [self.pm.xlist, self.pm.ylist]
		self.SpecialRooms				= {}
		self.Index_Holder               = {}
		self.Units_Placeholder          = {int(i):{} for i in self.pm.building_ids} #{building_id: {roomid: unit_obj}} {1: {17:unit_obj,18:unit_obj}}
		self.People_In_Buildings        = [0]*(self.Total_Num_Buildings)  #{day1:{buildingid: {0:0,1:2,,,,,,23:
		self.out_of_campus_unit = None
		self.hostels                    ={}
		# Campus Citizens
		self.Students 					= []
		self.Profs						= []
		self.Staff						= []
		self.Workers					= []
		self.all_people					= []
		self.Family_list 				= []
		self.visitors					= []

		self.hall_members               = {}

		#isolation and quarantine halls in a campus
		self.isolation_centre_ids = self.pm.isolation_centre
		self.quarantine_centre_ids = self.pm.quarantine_centre

		self.__get_Virus_constants__() # get virus constants (calibration of transmission rates)

	def __get_Virus_constants__(self):
		"""
		Calibrates the virus constant using calibration.py
		"""
		#self.VirusC = calibrate(self.pm)
		pass

	def initialize_campus(self):
		"""
		Initializes the campus by calling different functions to initialize
		"""
		self.__initialize_sectors__()
		self.__initialize_buildings__()
		self.__initialize_units__()

		self.__init_students__()
		# for p in self.Students:
		# 	for day in p.timetable:
		# 		for t in p.timetable[day]:
		# 			if p.timetable[day][t] != p.residence_unit and p.timetable[day][t].Sector != "Mess":
		# 				print(p.ID,day,t,p.timetable[day][t].Sector)
		# self.__init_profs__(start_id=self.last_student_id+1)
		# self.__init_staff__(start_id=self.last_prof_id+1) # Non Teaching Staff
		# self.__init_desk_workers__(start_id=self.last_staff_id+1)
		# self.__init_non_desk_workers__(start_id=self.last_desk_worker_id + 1)
		# self.__init_family__(start_id=self.last_staff_id+1)

		self._init_hostels_()

		self.all_people = []


		self.all_people.extend(self.Students)
		self.all_people.extend(self.Profs)
		self.all_people.extend(self.Staff)
		self.all_people.extend(self.Workers)
		self.all_people.extend(self.Family_list)
		self.attribute_matrix = [[0 for j in self.all_people] for i in self.all_people]

		self.Total_people = self.all_people.copy()

		self.ID_to_person = {}
		for i in self.all_people:
			self.ID_to_person[i.ID] = i


		self.__common_attribute_matrix__()


		self.pm.pop_update(len(self.all_people))


		self.__create_default_visiting__()
		# print(self.__room2unit__("NR323").default_visiting)

		for person in self.all_people:
			person.update_objects(self)

	def __initialize_sectors__(self):
		"""
		Initializes all the sectors
		"""
		self.sectors = {'Academic': Academic(self.pm), 'Residence': Residence(self.pm), 'Restaurant': Restaurant(self.pm), 'Healthcare': Healthcare(self.pm), 'Market': Market(self.pm), 'Gymkhana':Gymkhana(self.pm), 'Grounds': Grounds(self.pm), 'Non_Academic': Non_Academic(self.pm), 'Guest_House': Guest_House(self.pm),'Mess': Mess(self.pm)}

	def __initialize_buildings__(self):
		"""
		Initializes all the buildings for each sector
		"""
		self.buildings = {}     # {id[i] : Buildings{}}
		for sector in self.sectors:
			for buildingid in self.sectors[sector].building_ids:
				index                      = self.pm.building_id_to_indx[buildingid]
				self.buildings[buildingid]   = Buildings(self.pm, index, sector, buildingid)

	def __initialize_units__(self):
		"""
		Initializes all the units for each building
		"""
		special_rooms = self.pm.special_rooms
		k = 0
		for sector in self.sectors:
			for building in self.sectors[sector].building_ids:
				indx = self.pm.building_id_to_indx[building]
				self.Index_Holder[building] = k
				temp_special_rooms = special_rooms.get(self.pm.building_name[indx], False)

				if (self.Number_Units_per_floor[indx]>0):

					for j in range(len(self.Floor[indx])):
						if temp_special_rooms:
							floor_no = self.Floor[indx][j]
							if temp_special_rooms.get(floor_no,False) and len(temp_special_rooms[floor_no]):
								special_room_name = temp_special_rooms[floor_no].popitem()[0]
							else:
								special_room_name = None
						else:
							special_room_name = None

						self.sectors[sector].Units_list[building][k] = self.buildings[building].Building_units_list[k] = self.Units_Placeholder[building][k] = Unit(k,building,self.Number_Workers[indx],self.Floor[indx][j],self.Location[0][indx][j],self.Location[1][indx][j],sector,self.sectors[sector].room_area[building],capacity=self.pm.capacity[indx][k-self.Index_Holder[building]])

						if special_room_name != None:
							self.__create_special_rooms__(building,special_room_name,k)

						k+=1
			try:
				self.sectors[sector].generate_unoccupied_rooms_list(self.pm)
			except:
				pass
		self.out_of_campus_unit = Unit(-1,None,None,None,0,0,None,0)

	# def __create_named_rooms__(self,temp_room_code,indx,j,building,k):
	# 	"""
	# 	Used for giving the room names for the units initialized
	# 	"""
	# 	if self.pm.special_rooms != None:
	# 		try:
	# 			self.Rooms[list(self.pm.special_rooms[temp_room_code].keys())[j]] = self.Units_Placeholder[building][k]
	# 		except:
	# 			self.Rooms[temp_room_code+str(j)] = self.Units_Placeholder[building][k]
	# 	elif len(temp_room_code) != 0:
	# 		some_temp_no = int(j/(len(self.Floor[indx])//len(self.RoomCodes[-1])))
	# 		if some_temp_no >= len(self.RoomCodes[-1]): some_temp_no = len(self.RoomCodes[-1])-1
	# 		roomcode = self.RoomCodes[-1][some_temp_no]
	# 		self.Rooms[roomcode+str(j-((len(self.Floor[indx])//len(self.RoomCodes[-1])))*some_temp_no)]=self.Units_Placeholder[building][k]


	def __create_special_rooms__(self, building_id, SpecialName, unit_id):
		self.SpecialRooms[SpecialName] = self.Units_Placeholder[building_id][unit_id]

	def __init_students__(self):
		"""
		For initializing people & giving them their respective schedules
		"""

		self.student_details = pd.DataFrame(self.pm.Database["students"].find({"campusname": self.pm.CampusName}))
		if len(self.student_details) == 0:
			self.__create_student_details__()
			self.student_details = pd.DataFrame(self.pm.Database["students"].find({"campusname": self.pm.CampusName}))

		for i in range(len(self.student_details)):
			ageclass = 0
			mess_building_id = self.pm.df.loc[self.pm.df['BuildingName'] == self.student_details["MessBuildingName"][i], "BuildingID"].iloc[0]
			hall = self.pm.df.loc[self.pm.df['BuildingName'] == self.student_details["HostelBuildingName"][i], "BuildingID"].iloc[0]
			room = random.choice(self.sectors["Residence"].non_occupied_rooms["Student Residence"][hall])
			self.__update_unit_occupancy__("Student Residence",hall,room)
			junta = student(Campus=self, role="student", ID=i, age=self.student_details["Age"][i], ageclass=ageclass, year=self.student_details["Year"][i],courses_list=self.student_details["Courses"][i], dept=self.student_details["Department"][i], residence=[hall, room-self.Index_Holder[hall]],batch=self.student_details["Batch"][i], prog=self.student_details["Program"][i], mess_building_id=mess_building_id, mess_no= None, inCampus=self.student_details["inCampus"][i], lab_code = None)
			self.Students.append(junta)
			self.pm.Population_Dist[ageclass] += 1

			if self.hall_members.get(junta.residence_building_id,-1) == -1:
				self.hall_members[junta.residence_building_id] = []
			self.hall_members[junta.residence_building_id].append(junta.ID)

		self.last_student_id = len(self.student_details) - 1





	def __init_profs__(self, start_id):
		"""
		Initializes profs and generates their schedules

		Args:
			start_id : This is the first id of the profs
		"""
		prof_details = pd.DataFrame(self.pm.Database["faculties"].find({"campusname": self.pm.CampusName}))
		for i in range(len(prof_details)):
			residence_building_id = self.pm.df.loc[self.pm.df['BuildingName'] == prof_details["ResidenceBuildingName"][i], "BuildingID"].iloc[0]
			residenceunitid = random.choice(self.sectors["Residence"].non_occupied_rooms["Faculty Residence"][residence_building_id])
			self.__update_unit_occupancy__("Faculty Residence", residence_building_id, residenceunitid)
			dept = prof_details['Department'][i]
			prof = professor(Campus=self, residence_unit_id=residenceunitid ,residence_building_id=residence_building_id, ID=start_id + i, dept=dept,courses_list=prof_details["Courses"][i], adult_family_members=prof_details['AdultFamilyMembers'][i] , child_family_members = prof_details["NoofChildren"][i])
			self.Profs.append(prof)
			self.pm.Population_Dist[3] += 1

		self.last_prof_id = start_id + len(prof_details) - 1


	def __init_staff__(self, start_id):
		"""
		Initializes staff and loads them with their parameters

		Args:
			start_id : This is the first id of the staff
		"""

		staff_details = pd.DataFrame(self.pm.Database["staffs"].find({"campusname": self.pm.CampusName}))

		for i in range(len(staff_details)):
			residence_building_id = self.pm.df.loc[self.pm.df['BuildingName'] == staff_details["ResidenceBuildingName"][i],"BuildingID"].iloc[0]
			workplace_buildingid = self.pm.df.loc[self.pm.df['BuildingName']  == staff_details["WorkplaceBuildingName"][i],"BuildingID"].iloc[0]
			residenceunitid = random.choice(self.sectors["Residence"].non_occupied_rooms["Staff Residence"][residence_building_id])
			self.__update_unit_occupancy__("Staff Residence",residence_building_id,residenceunitid)
			if staff_details["StaffCategory"][i] == 1:
				staff_person = staff(Campus=self,residence_unit_id=residenceunitid, prob_to_go_out=0,residence_building_id=residence_building_id , ID=start_id + i, workplace_buildingid=workplace_buildingid , adult_family_members = staff_details['AdultFamilyMembers'][i] , child_family_members = staff_details["NoofChildren"][i])
			elif staff_details["StaffCategory"][i] == 2:
				desk_worker_building_ids = random.choices(list(self.buildings.keys()), k=1)
				unit_id = random.choice(list(self.Units_Placeholder[desk_worker_building_ids].keys()))
				staff_person = deskWorker(Campus=self, ageclass=3, ID=start_id + i ,work_building_id=workplace_buildingid,residence_unit=residenceunitid,work_building_unit=self.Units_Placeholder[desk_worker_building_ids][unit_id],inCampus=1)
			else:
				staff_person = nonDeskWorker(Campus=self, ageclass=3, ID=start_id + i,residence_unit=residence_building_id, work_building_id=workplace_buildingid,inCampus=1)

			self.Staff.append(staff_person)
			self.pm.Population_Dist[3] += 1
		self.last_staff_id = start_id + len(staff_details) - 1

	def __init_desk_workers__(self,start_id):
		if self.pm.CampusName == "IIITH":
			ctr = 0
			num_security = self.pm.num_security
			num_desk_workers = self.pm.num_tot_desk_workers
			desk_worker_building_ids = random.choices(list(self.buildings.keys()),k=num_desk_workers)
			for building_id in desk_worker_building_ids:
				unit_id = random.choice(list(self.Units_Placeholder[building_id].keys()))
				desk_worker_person = deskWorker(Campus=self, ageclass=3, ID=start_id + ctr,work_building_id=building_id,residence_unit=self.out_of_campus_unit,work_building_unit=self.Units_Placeholder[building_id][unit_id],inCampus=1)
				self.Workers.append(desk_worker_person)
				ctr += 1
			security_ids = random.choices(list(self.buildings.keys()),k=num_security)
			for building_id in security_ids:
				unit_id = random.choice(list(self.Units_Placeholder[building_id].keys()))
				desk_worker_person = deskWorker(Campus=self, ageclass=3, ID=start_id + ctr,work_building_id=building_id, residence_unit=self.out_of_campus_unit,work_building_unit=self.Units_Placeholder[building_id][unit_id],inCampus=1)
				self.Workers.append(desk_worker_person)
				ctr += 1
			ctr -= 1
			self.last_desk_worker_id = start_id+ctr
			return
		ctr = 0
		k=0
		for building_id in self.Units_Placeholder.keys():
			if(len(self.Units_Placeholder[building_id])>1):
				for unit_id in random.sample(self.Units_Placeholder[building_id].keys(),self.pm.num_desk_workers):
					desk_worker_person = deskWorker(Campus=self,ageclass=3,ID=start_id+ctr, work_building_id=building_id,residence_unit=self.out_of_campus_unit, work_building_unit=self.Units_Placeholder[building_id][unit_id],inCampus=1)
					self.Workers.append(desk_worker_person)
					ctr += 1
		ctr -= 1
		self.last_desk_worker_id = start_id+ctr

	def __init_non_desk_workers__(self,start_id):
		if self.pm.CampusName == "IIITH":
			ctr = 0
			num_house_keeping = self.pm.num_house_keeping
			num_mess = self.pm.num_mess
			num_non_desk_workers = self.pm.num_tot_non_desk_workers
			non_desk_building_ids = random.choices(list(self.buildings.keys()),k=num_non_desk_workers)
			for building_id in non_desk_building_ids:
				non_desk_worker = nonDeskWorker(Campus=self, ageclass=3, ID=start_id + ctr,residence_unit=self.out_of_campus_unit, work_building_id=building_id,inCampus=1)
				self.Workers.append(non_desk_worker)
				ctr += 1
			mess_building_ids = random.choices(self.sectors['Mess'].building_ids,k=num_mess)
			for building_id in mess_building_ids:
				non_desk_worker = nonDeskWorker(Campus=self, ageclass=3, ID=start_id + ctr,residence_unit=self.out_of_campus_unit, work_building_id=building_id,inCampus=1)
				self.Workers.append(non_desk_worker)
				ctr += 1
			house_keeping_building_ids = random.choices(self.sectors['Residence'].building_ids, k=num_house_keeping)
			for building_id in house_keeping_building_ids:
				non_desk_worker = nonDeskWorker(Campus=self, ageclass=3, ID=start_id + ctr,residence_unit=self.out_of_campus_unit, work_building_id=building_id,inCampus=1)
				self.Workers.append(non_desk_worker)
				ctr += 1
			ctr -= 1
			self.last_non_desk_worker_id = start_id + ctr
			return
		ctr = 0
		k=0
		for building_id in self.Units_Placeholder.keys():
			for i in range(self.pm.workers_per_building):
				if (len(self.Units_Placeholder[building_id]) > 0):
					non_desk_worker = nonDeskWorker(Campus=self,ageclass=3,ID=start_id+ctr,residence_unit=self.out_of_campus_unit, work_building_id=building_id, inCampus=1)
					self.Workers.append(non_desk_worker)
					ctr += 1
		ctr -= 1
		self.last_non_desk_worker_id = start_id+ctr

	def __init_family__(self,start_id):
		for people in self.Profs:
			fam = Family(people, school_id = 19 ,adult_family_members = people.adult_family_members,child_family_members = people.child_family_members)
			for family_member in fam.family:
				family_member.ID = start_id
				self.Family_list.append(family_member)
				people.Family_list_obj.append(family_member)
				start_id+=1
		for people in self.Staff:
			fam = Family(people, school_id = 19 ,adult_family_members = people.adult_family_members,child_family_members = people.child_family_members)
			for family_member in fam.family:
				family_member.ID = start_id
				self.Family_list.append(family_member)
				people.Family_list_obj.append(family_member)
				start_id+=1

	def __room2unit__(self, room_name):
		"""
		This function is used for returning unit object

		Args :
			room_name : Name of the room

		Returns :
			Object of the room
		"""
		if room_name[0] == 'V':
			code = room_name[0]
			number = room_name[1:]
		else:
			code = room_name[0:2]
			if code == 'NC':
				allrooms=['NC131', 'NC132', 'NC141', 'NC142', 'NC231', 'NC232', 'NC233', 'NC234', 'NC241', 'NC242', 'NC243', 'NC244', 'NC331', 'NC332', 'NC333', 'NC334', 'NC341', 'NC342', 'NC343', 'NC344', 'NC431', 'NC432', 'NC433', 'NC434', 'NC441', 'NC442', 'NC443', 'NC444']
				number = str(allrooms.index(room_name))
			elif code == 'NR':
				allrooms=['NR121', 'NR122', 'NR123', 'NR124', 'NR221', 'NR222', 'NR223', 'NR224', 'NR321', 'NR322', 'NR323', 'NR324', 'NR421', 'NR422', 'NR423', 'NR424']
				number = str(allrooms.index(room_name))
			elif code == 'S-':
				allrooms = ['S-123', 'S-125', 'S-126', 'S-127', 'S-136', 'S-216', 'S-122A', 'S-301', 'S-302']
				number = str(allrooms.index(room_name))
			elif len(room_name) == 5 and room_name[3]=='L':
				number = str(int(room_name[2]+room_name[4])-20)
			else:
				number = room_name[2:]
				#print(code+number)
		return self.Rooms[code+number]

	def __get_person_obj__(self, idx):
		"""
		This functon is used for returning the person object

		Args :
			idx : Index of the person

		Returns :
			The object of the person
		"""
		return self.ID_to_person[idx]


	def __create_default_visiting__(self):
		"""
		Creates a dictionary of usual occupancy f unit throughout the week
		"""
		for person in self.all_people:
			for day in person.timetable:
				for t in person.timetable[day]:
					if type(person.timetable[day][t]) == dict:
						continue
					if person.timetable[day][t].default_visiting[day].get(t,-1) == -1:
						person.timetable[day][t].default_visiting[day][t] = (person.ID,)
					else:
						person.timetable[day][t].default_visiting[day][t]+=(person.ID,)
	def __common_attribute_matrix__ (self):
		k = 0
		for i in self.all_people:
			l = k
			for j in self.all_people[l:]:
				if i == j :
					self.attribute_matrix[i.ID][j.ID] = 0
					k += 1
					continue
				count = 0
				if (i.dept == j.dept ):
					count = count + 1
				if (i.year == j.year ):
					count = count + 1
				if (i.Role==j.Role and i.Role == "student"):
					if(i.prog == j.prog):
						count = count + 1
					if(i.mess_unit == j.mess_unit):
						count += 1
					if i.batch == j.batch:
						count+=1
					for course in i.courses_list:
						if course in j.courses_list:
							count+=1
				if hasattr(i,"residence_building_id") and hasattr(j,"residence_building_id"):
					if (i.residence_building_id == j.residence_building_id ):
						count = count + 1
				if hasattr(i, "residence_unit") and hasattr(j, "residence_unit"):
					if (i.residence_unit == j.residence_unit ):
						count = count + 1
				#print(i.ID,j.ID)
				self.attribute_matrix[i.ID][j.ID] = count
				self.attribute_matrix[j.ID][i.ID] = count
				l += 1
			k += 1

		#print(self.attribute_matrix)

	def init_asymptomatic(self,sample_persons):
		"""
		Infect people initially as required
		"""
		count = 0
		while count < self.asymptomatic:
			person = sample_persons.pop()

			if self.pm.Verbose:
				print('Infected person {} who is a {} initially'.format(person.ID, person.Role))
			self.__infect_person__(person)

			count+=1

	def init_symptomatic(self,sample_persons):
		count = 0
		while count < self.symptomatic:
			person = sample_persons.pop()
			if person.is_Out_of_Campus() ==False:
				if person.is_Healthy() == True :
					Symptom = 0
					self.Symptom_placeholder[Symptom].append(person)
					person.infected()
			count+=1

	def init_recovered(self,sample_persons):
		count = 0
		while count < self.recovered:
			person = sample_persons.pop()
			person.State = 'Symptomatic'
			self.Recovered_Placeholder[0].append(person)

			count+=1

	def init_partially_vaccinated(self,sample_persons):
		count = 0
		while count < self.partially_vaccinated:
			person = sample_persons.pop()
			person.Gets_First_Dose()
			self.Num_Vaccinated_Once += 1
			count+=1

	def init_fully_vaccinated(self,sample_persons):
		count = 0
		while count < self.fully_vaccinated:
			person = sample_persons.pop()
			person.Vaccination_State = "Partially_Vaccinated"
			person.Gets_Second_Dose()
			self.Num_Vaccinated_Twice += 1
			count+=1


	def _init_hostels_(self):
		for student in self.Students:
			if self.hostels.get(student.residence_unit.Building, -1) == -1:
				self.hostels[student.residence_unit.Building] = []
			self.hostels[student.residence_unit.Building].append(student.ID)

	def __create_student_details__(self):
		batch_values = self.pm.strength_distribution
		batchwise_course_distribution = self.pm.course_distribution
		residence_building_name = list(self.pm.df[self.pm.df["BuildingType"] == 'Student Residence'].iloc[:, 3])
		weights = []
		for i in residence_building_name:
			weights.append(int(self.pm.df.loc[self.pm.df['BuildingName'] == str(i), "NumberofRoomsinEachFloor"].iloc[0])*int(self.pm.df.loc[self.pm.df['BuildingName'] == str(i), "NoOfFloors"].iloc[0]))
		ctr = 1
		a = []
		for batch in batch_values:
			year = batch_values[batch]["year"]
			for j in range(batch_values[batch]["strength"]):
				age = str(18 + (year-1)+random.choice([0,1]))
				ran = random.choices(range(len(residence_building_name)),weights)[0]
				weights[ran]-=1
				hostel = random.choices(residence_building_name, weights)[0]
				mess = random.choice(list(map(str,list(self.pm.df[self.pm.df["BuildingType"] == "Mess"].iloc[:,3]))))
				strength = self.pm.strength_distribution[batch]['strength']
				try:
					dist = batchwise_course_distribution[batch]
					courses_list = select_courses(strength,dist)
				except:
					courses_list = []
				a.append({"StudentID": ctr, "Age": int(age), "HostelBuildingName":hostel, "MessBuildingName":mess, "Year":int(year), "Department":batch_values[batch]["department"], "Program":batch_values[batch]["program"], "Batch":batch, "inCampus":1,"Courses":courses_list,"campusname":self.pm.CampusName})
				ctr+=1
		self.pm.Database["students"].insert_many(a)
		print(ctr)
		filter_applied = {"campusname": self.pm.CampusName}
		new_value_set = {"$set": {'Student': ctr}}
		self.pm.Database["counters"].update_one(filter_applied, new_value_set)


	def __update_unit_occupancy__(self,ResidenceType,Building_Id,Unit_Id):
		assert self.Units_Placeholder[Building_Id][Unit_Id].occupancy <= self.Units_Placeholder[Building_Id][Unit_Id].capacity
		self.Units_Placeholder[Building_Id][Unit_Id].occupancy += 1

		if self.Units_Placeholder[Building_Id][Unit_Id].occupancy == self.Units_Placeholder[Building_Id][Unit_Id].capacity:
			self.sectors["Residence"].non_occupied_rooms[ResidenceType][Building_Id].remove(Unit_Id)
