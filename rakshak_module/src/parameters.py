import os
import json
import random
import time

import numpy as np
import pandas as pd
from pyproj import Geod
from shapely.geometry import Polygon, Point

from .map_utils import random_points_in_polygon, cal_coordinates

geod = Geod(ellps="WGS84")

class Virus_Parameters:
	"""
	All virus related parameters

	Args :
		**kwargs                    : Key word arguments(optional)
	"""

	def __init__(self, **kwargs):

		self.Virus_Name 			    = "CoronaVirus"
		self.Virus_R0 				    = kwargs.get("Virus_R0", 1.0)
		self.Virus_c					= 1
		self.Initial_Compliance_Rate 	= kwargs.get("Compliance Rate",1)

		self.Virus_Params = {
			'Education'	: {'Time':4,    'Distance':2.5},
			'Office'	: {'Time':8,    'Distance':2},
			'Commerce'	: {'Time':8,    'Distance':2},
			'Healthcare': {'Time':0,    'Distance':2},
			'Transport' : {'Time':1,    'Distance':1},
			'Home' 		: {'Time':16,   'Distance':1},
			'Grocery'	: {'Time':0.5,  'Distance':4},
			'Unemployed': {'Time':8,    'Distance':1},
			'Random'	: {'Time':1,    'Distance':2},
			}

		self.Social_Distancing_Factor = kwargs.get("Social_Distancing_Factor", 1)
		for key in self.Virus_Params:
			self.Virus_Params[key]["Distance"] *= self.Social_Distancing_Factor

		self.Virus_DistanceDist 		= {"Constant": 0.128, "Ratio": 2.02}
		self.Virus_Deathrates 			= kwargs.get("Virus_Deathrates", [0.01/2,0.005/2,0.01/2,0.01/2,0.04/2,0.30/2]) # Between age groups in agedist model
		self.Virus_IncubationPeriod		= kwargs.get("Virus_IncubationPeriod", [6,6,8,5,2,2]) # Between Age groups
		self.Virus_ExpectedCureDays		= kwargs.get("Virus_ExpectedCureDays", 14) # Days to cure
		self.Virus_FullCapRatio 		= kwargs.get("Virus_FullCapRatio", [5/3,5/3,5/3]) # When hopitals are overwhelmed by how much propertion deathrateincreases
		self.Virus_PerDayDeathRate		= [EE/self.Virus_ExpectedCureDays for EE in self.Virus_Deathrates]

		self.Virus_ProbSeverity 		= kwargs.get("Virus_ProbSeverity", [[0.70,0.26,0.04],
																			[0.80,0.16,0.04],
																			[0.80,0.16,0.04],
																			[0.95,0.04,0.01],
																			[0.60,0.30,0.10],
																			[0.40,0.40,0.20],
																			[0.10,0.40,0.50]])  # Mild, Medicore, Severe between Age Groups

		self.Sector_Mask_Fraction = { # This is the factor by which inter-person distance is multiplied for each sector (due to the effect of masks)
			'Education' 	: 1, #1.5,
			'Office' 	: 1, #2,
			'Commerce' 	: 1, #1.5,
			'Healthcare'	: 1, #2,
			'Transport' 	: 1, #2,
                        'Home'          : 1,
                        'Grocery'       : 1, #1.5,
                        'Unemployed'	: 1,
                        'Random'        : 1 #1.5
			}


		self.Comorbidty_matrix = {
		'ComorbidX' 	: [0.00,0.00,0.00,0.00,0.00,0.00] 	# Percentage of Population getting deasese X
		}

		self.Comorbidty_weights = {#self.pm.duration
		'ComorbidX' 	: [0.1,0.7,0.2] 					# Probablity of increase in Severtiy if you have Disease X
		}

		self.Quarantine_Period = kwargs.get("Quarantine_Period", 14)

		# Vaccination Parameters 
		self.Num_Daily_Vaccinations = 5
		self.Efficiency_Dose_1		= 0.65
		self.Efficiency_Dose_2		= 0.95

		# Paradigms Currently Implemented - [None, "Random_Sampling"]
		self.Vaccination_Paradigm 	= kwargs.get("Vaccination_Paradigm", None)
		self.Second_Dose_Threshold	= kwargs.get("Second_Dose_Threshold", 0.1) # Fraction of people who have to receive one dose before anyone can receive two

		self.outside_infection_prob = kwargs.get("outside_infection_prob",0)

		self.avg_interpdist_bldg_transmission = kwargs.get("avg_interpdist_bldg_transmission", 1)
		self.avg_exptime_bldg_transmission    = kwargs.get("avg_exptime_bldg_transmission", 1/12)


	def get_virus_c_value(self,Calc_R0=None):
		if Calc_R0 != None:
			self.Virus_c = self.Virus_R0/Calc_R0
			return
		# try:
		# 	with open("data_"+self.CampusName+"/Calculated_R0.txt",'r') as fh:
		# 		line = fh.readline()
		# 		self.Virus_c = self.Virus_R0/float(line.split("=")[1])
		# except FileNotFoundError:
		# 	print("data_"+self.CampusName+"/Calculated_R0.txt is not found.")


class Spatial_Parameters:
	"""
	All campus spatial map related parameters are loaded from the files in Campus_data folder

	Args :
        ShpFile              : Shapefile of all buildings
		OtherFile            : Building data_IITKGP
		StrengthData         : Population
		ClassRooms           : Classroom names and capacity
		CampusName           : Name of the campus
	"""
	def __init__(self, CampusName):

		self.CampusName	= CampusName
		self.Database	= self.Client['testdb2']

		self.strength_distribution = {doc['BatchCode']: {"year": doc['YearOfStudy'],"department": doc['Department'],"program": doc['ProgramCode'],"strength": doc['Strength']} for doc in self.Database['batchstudents'].find({"campusname": self.CampusName})}

		self.course_distribution = {}
		self.courses_time_location = {}
		for doc in self.Database['classschedules'].find({"campusname": self.CampusName}):
			class_timings = {}
			ctr = 1
			for day_obj in doc["ClassDays"]:
				day = day_obj["Day"]
				times = list(range(int(day_obj["Timing"]["start"]), int(day_obj["Timing"]["end"])))
				for t in times:
					class_timings[ctr] = [day, str(t)+"-"+str(t+1)]
					ctr += 1
			if not doc.get("RoomName", False):  # if there is no room for this course, assigning None
				self.courses_time_location[doc["CourseID"]] = {"room": None, "timings": class_timings}
			else:  # if room is mentioned in the database it is assigned
				self.courses_time_location[doc["CourseID"]] = {"room": doc["RoomName"], "timings": class_timings}
			if not len(doc['StudentComposition']):
				continue
			for batch_obj in doc['StudentComposition']:
				batch_code = batch_obj['BatchCode']
				strength = batch_obj['Count']
				if self.course_distribution.get(batch_code, False):
					self.course_distribution[batch_code].update({doc['CourseID']: str(strength)})
				else:
					self.course_distribution[batch_code] = {doc['CourseID']: str(strength)}


		self.Departments                            = list(set([self.strength_distribution[i]['department'] for i in self.strength_distribution]))   # Department and year wise strength of students


		self.special_rooms = {}

		self.Number_Workers                             = []
		self.Floor                                      = []
		self.capacity 									= []

		if self.Client==None:
			print("Not connected to Database")
			assert False
		self.df = pd.DataFrame(self.Database['campusbuildings'].find({"campusname": self.CampusName}))
		self.building_name = list(self.df['BuildingName'])
		ctr = 0
		for build in self.building_name:
			self.capacity.append([])
			temp_room_objs = self.df.loc[self.df['BuildingName'] == build, 'Rooms'].iloc[0]
			for obj in temp_room_objs:
				if obj['RoomName'][:8] != "RoomName":
					if not self.special_rooms.get(build, False):
						self.special_rooms[build] = {obj["Floor"]: {obj["RoomName"]: obj["Capacity"]}}
					elif not self.special_rooms[build].get(obj["Floor"], False):
						self.special_rooms[build][obj["Floor"]] = {obj["RoomName"]: obj["Capacity"]}
					else:
						self.special_rooms[build][obj["Floor"]][obj["RoomName"]] = obj["Capacity"]
				self.capacity[ctr].append(obj["Capacity"])

			ctr+=1

		self.building_ids = list(self.df['BuildingID'])
		self.building_id_to_indx = {int(self.building_ids[i]): i for i in range(len(self.building_name))}
		self.rooms_packing_fraction = [0.6 for i in range(len(self.building_name))]  # Whenever this is changed calibration has to be done again
		self.description = list(self.df['BuildingType'])

		self.sectors = list(set(self.description))

		self.coordinates = [[[float(c) for c in cstr.split()] for cstr in cor_str.split(",")] for cor_str in list(self.df['BuildingCoordinates'])]

		self.polygons = [Polygon(cor) for cor in self.coordinates]


		self.rooms                                      = []
		self.num_rooms_per_floor                        = list(self.df['NumberofRoomsinEachFloor'])
		self.heights                                    = list(self.df['NoOfFloors'])
		self.xlist = []
		self.ylist = []
		self.Total_area = sum([abs(geod.geometry_area_perimeter(polyg)[0]) for polyg in self.polygons])

		self.Population_groups 	=  [5,18,25,60,80,150]                   #Max ages of different groups
		self.Population			=  0 #Total population; has to be updated later
		self.Population_Dist	=  [0,0,0,0,0,0]  #population distribution corresponding to the above groups #TODO: will be filled later in Campus_Model but has to be given here itself
		self.Family_size		=  [3.5]  #TODO: remove the hardcoding

		self.population_in_lakh 					= self.Population/100000 #Per lakh

		#-------------------------- Transaction  Parameters ------------------------------------------
		#============================================================================================
		self.Transaction_ProbablityOfPurchase 	= 0.5
		#--------------------------- Transport Parameters ------------------------------------------
		#============================================================================================
		#Transporation Model PerDay Model

		# self.ExpStops 		= 4
		# self.VarStops 		= 1
		self.NumBuses 		= int(250*self.population_in_lakh) #written here but will be 0 and will be updated by another function call
		# self.NumRoutes		= int(30*population_in_lakh)
		self.Prob_use_TN	= 0.17


		self.__cal_rooms__()

		self.__assign_coords__()

		self.__assign_remaining__()


	def pop_update(self,population):
		self.Population = population
		self.population_in_lakh = population/100000
		self.NumBuses = int(250*self.population_in_lakh)



	def __assign_remaining__(self):
		"""
		This function assigns the remaining attributes like Number_Workers, Floor etc.
		"""
		for i in range(len(self.building_name)):
			self.Number_Workers.append(self.df.loc[self.df['BuildingName']==self.building_name[i], 'NoOfWorkers'].iloc[0])
			self.Floor.append([])

			for j in range(1, self.heights[i]+1):
				for k in range(self.num_rooms_per_floor[i]):
					self.Floor[i].append(j)


	def __assign_coords__(self):
		"""
		This function assigns coordinates to the buildings which are generated using __cal_rooms__
		"""
		j = 0
		for buil in self.rooms:
			self.xlist.append([i.x for i in buil])
			self.ylist.append([i.y for i in buil])
			j+=1

	def __cal_rooms__(self):
		"""
		Assigns coordinates to each unists by calling other functions

		Args :
			no_rooms        : number of rooms of each building
		"""
		for i in range(len(self.building_name)):
			points = random_points_in_polygon(self.heights[i]*self.num_rooms_per_floor[i],self.polygons[i])
			self.rooms.append(points)
		return


class Parameters(Virus_Parameters, Spatial_Parameters):
	"""
	All Parameters

	Args :
		**kwargs                    : Key word arguments(optional)
	"""
	def __init__(self, **kwargs):

		CampusName = kwargs.get("Campus", "IIT Jodhpur")

		self.Population_Fractions = kwargs.get("Population_Fractions")
		self.Client = kwargs.get("MongoClient",None)
		Virus_Parameters.__init__(self, **kwargs)
		Spatial_Parameters.__init__(self, CampusName)

		self.SIM_DAYS = kwargs.get("SIM_DAYS", 60)
		self.SIM_START_TIME = kwargs.get("SIM_START_TIME", None)

		self.result_resolution = kwargs.get("Result Resolution by hours", 1)

		self.SaveMovementSnapshots = kwargs.get("SaveMovementSnapshots", False)

		# self.num_security = kwargs.get("num_security", 43)
		# self.num_tot_desk_workers = kwargs.get("num_tot_desk_workers", 50)
		# self.num_house_keeping = kwargs.get("num_house_keeping", 25)
		# self.num_mess = kwargs.get("num_mess", 62)
		# self.num_tot_non_desk_workers = kwargs.get("num_tot_non_desk_workers", 50)

		#External Visitor Parameters
		self.Daily_Visitors = kwargs.get("Daily_Visitors", 10)
		self.avg_visiting_days = kwargs.get("avg_visiting_days", 2)
		self.num_desk_workers = kwargs.get("num_desk_workers", 2)
		self.workers_per_building = kwargs.get("workers_per_building", 2)

		# Testing Parameters
		self.Exact_Test_Details = {}

		testing_strategy_mapping = {'Complete Random':1, 'Symptomatic First':2, 'Symptomatic First then Hostel-wise Random':3, 'Perfect Contact Tracing':4,
		 'Risk-based Contact Tracing':5}
		self.testing_strategy = testing_strategy_mapping[kwargs.get("Testing_Strategy", 'Symptomatic First')[0]]

		self.Test_sample_start = kwargs.get("Test_sample_start_day",1)

		self.is_calibrated = kwargs.get("is_calibrated",False)

		self.Testing_capacity = kwargs.get("Testing_capacity",34)
		self.Testing_days     = kwargs.get("Testing_days",['sunday','monday','tuesday','wednesday','thursday','friday','saturday'])
		self.test_sensitivity = kwargs.get("Test_Sensitivty", 0.95)
		self.test_specificity = kwargs.get("Test_Specificity", 1)
		self.retesting_negative_people = kwargs.get('retesting_negative_people',True)
		self.retesting_positive_people_14_days_back = kwargs.get("retesting_positive_people_14_days_back",True )
		self.selecting_random_people = kwargs.get('selecting_random_people' , True)
		self.selecting_retest_random_people = kwargs.get('selecting_retest_random_people', True)
		self.SimName = kwargs.get("SimName", "")
		self.Verbose = kwargs.get("Verbose", True)
		self.SAVEDIR = kwargs.get("results_path",os.path.join("results", self.SimName))
		os.makedirs(self.SAVEDIR, exist_ok=True)

		self.isolation_centre = kwargs.get("isolation_centre",[])
		self.quarantine_centre = kwargs.get("quarantine_centre",[])
		self.is_dorfman_pooling = kwargs.get("Dorfman_Pooling", False)

		#initial_case_statistics
		self.init_case_statistics = kwargs.get("init_case_statistics",
											   {'Asymptomatic': 12,
												'Symptomatic': 0,
												'Recovered': 0,
												'Partially_Vaccinated': 0,
												'Fully_Vaccinated': 0})

		self.common_areas_info = {}

		self.Lockdown_Areas = kwargs.get("Lockdown_Areas", ["No Lockdown"])
		if "No Lockdown" in self.Lockdown_Areas:
			self.Lockdown_Areas.remove("No Lockdown")

		"""
		#shutdown_strategy
		# for start and end conditions the first number denotes the type and the second number denotes the threshold
		# Types:
		# 0		-> no_lockdown
		# 1		-> daily_positive_cases
		# [2,n]	-> cum_positive_cases over last n days
		# 3		-> testing_queue_size
		# 4		-> at_risk_people  TODO: yet to be done

		# for example:
		# self.shutdown_strategy = {
		# 						  'sectors': {'Academic':		{'start_criterion': [1,0], 'duration':7, 'end_criterion': [1,0], 'roles': ['student']},
		# 									 'Restaurant':		{'start_criterion': [0,10], 'duration':7, 'end_criterion': [1,0], 'roles': ['student','faculty','staff']},
		# 									 'Market':			{'start_criterion': [0,10], 'duration':7, 'end_criterion': [1,0], 'roles': ['student']},
		# 									 'Gymkhana':		{'start_criterion': [0,10], 'duration':7, 'end_criterion': [1,0], 'roles': ['student','faculty']},
		# 									 'Grounds':			{'start_criterion': [0,10], 'duration':7, 'end_criterion': [1,0], 'roles': ['student','faculty']},
		# 									 'Non_Academic':	{'start_criterion': [0,10], 'duration':7, 'end_criterion': [1,0], 'roles': ['student','faculty']},
		# 									 'Guest_House':		{'start_criterion': [0,10], 'duration':7, 'end_criterion': [1,0], 'roles': ['student','faculty','staff']}},
		#
		# 						  'buildings':{5:				{'start_criterion': [0,0],  'duration':7, 'end_criterion': [0,0], 'roles': ['student']}}
		# 						  }
		"""

		self.shutdown_strategy = {'sectors': {}, 'buildings': {}}
		temp_sectors_possible_to_lock = {"Academic", "Restaurant", "Market", "Gymkhana", "Grounds", "Non_Academic", "Guest_House", "Mess"}
		for sector_building in self.Lockdown_Areas:
			if sector_building in temp_sectors_possible_to_lock:
				self.shutdown_strategy['sectors'][sector_building] = {'start_criterion': [1,0], 'duration': self.SIM_DAYS, 'end_criterion': [1,0], 'roles': ['student', 'faculty']}
			self.shutdown_strategy['buildings'][sector_building] = {'start_criterion': [1,0], 'duration': self.SIM_DAYS, 'end_criterion': [1,0], 'roles': ['student', 'faculty']}





class Contact_Graph_Parameters:
	"""
	Parameters used for the contact graph
	"""
	def __init__(self):
		self.duration 		= 14 # in days
		self.infectdist		= 1.8288 # in metres (infection radius, default value keep around 10)
		self.tstep 			= 3600 # the current timestep for activity data_IITKGP in seconds
		self.units 			= 10 #  maximum allowed units of tstep missing from the geo-coordinates data_IITKGP for imputation

