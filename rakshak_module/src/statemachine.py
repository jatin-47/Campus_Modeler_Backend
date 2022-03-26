import logging
from transitions import Machine
from functools import partial
import time

# TODO: whenever there is a state change store the following
# (DAY,function_called) -> Stored for every person for agent status, state and Testing state


class TestingState(object):

	"""Summary

	Attributes:
	    in_stack (bool): Description
	    machine (TYPE): Description
	    state (str): Description
	    tested (bool): Description
	"""
	Num_not_tested = None

	def __init__(self):
		"""This is responsible for updating testing state of the person

		Deleted Parameters:
		    person (object): Home object
		    VM (object): Virusmodel object
		"""

		super().__init__()
		# logging.getLogger('transitions').setLevel(logging.WARNING)
		self.state 		= 'Not_tested'

		self.machine = Machine(model=self,states=['Not_tested', 'Awaiting_Testing', 'Tested_Positive', 'Tested_Negative'],
									  initial='Not_tested',
									  transitions=[
										  {'trigger': 'awaiting_test',
										   'source': ['Not_tested', 'Awaiting_Testing', 'Tested_Negative','Tested_Positive'],
											   'dest': 'Awaiting_Testing','before': 'Update_Num_not_tested'},
										  {'trigger': 'tested_positive', 'source': 'Awaiting_Testing',
										   'dest': 'Tested_Positive', 'after': 'Update_TestingLog'},
										  {'trigger': 'tested_negative', 'source': 'Awaiting_Testing',
										   'dest': 'Tested_Negative', 'after': 'Update_TestingLog'}
									  ])

	def Update_Num_not_tested(self):
		if self.state == 'Not_tested':
			TestingState.Num_not_tested -= 1
		elif self.re_test == 1:
			TestingState.Num_not_tested -= 1

	def Update_TestingLog(self):
		curr_date = time.strftime("%m/%d/%Y",self.Campus.curr_timestamp)
		try:
			indx = self.Campus.TestingLog["Date of Testing"].index(curr_date)
			if self.state == "Tested_Positive":
				self.Campus.TestingLog["No of Student Positive"][indx] += 1
				self.Campus.TestingLog["Total Positive"][indx] += 1
			self.Campus.TestingLog["Number of Tests"][indx] += 1
			self.Campus.TestingLog["Number of Student's Tested"][indx] += 1

		except:
			self.Campus.TestingLog["Date of Testing"].append(curr_date)
			if self.state == "Tested_Positive":
				self.Campus.TestingLog["No of Student Positive"].append(1)
				self.Campus.TestingLog["Total Positive"].append(1)
			else:
				self.Campus.TestingLog["No of Student Positive"].append(0)
				self.Campus.TestingLog["Total Positive"].append(0)
			self.Campus.TestingLog["Number of Tests"].append(1)
			self.Campus.TestingLog["Number of Student's Tested"].append(1)



	# def add_to_TestingQueue(self, PrivateTest=False):
	# 	"""Summary
	# 	"""
	# 	# This function is for the region to add citizens into testingQueue
	# 	if PrivateTest == False:
	# 		if self.state == 'Not_tested':
	# 			self.Region.TestingQueue.append(self)
	#
	# 			#print('Region {} added person {}'.format(self.Region.Name, self.IntID))

	#pass type of test
	# def tested_positive_func(self, PrivateTest=False):
	# 	"""Summary
	# 	"""
	# 	self.Region.TestedP['Positive'].append(self)
	# 	self.Region.NumTestedPositive.value += 1
	#
	# 	if PrivateTest == False:
	# 		self.__remove_from_testing_list__()
	#
	# 	if self.is_quarantined():
	# 		self.isolate()

	#
	# def tested_negative_func(self, PrivateTest=False):
	# 	"""Summary
	# 	"""
	# 	self.Region.TestedP['Negative'].append(self)
	#
	# 	if PrivateTest == False:
	# 		self.__remove_from_testing_list__()
	#
	# def __remove_from_testing_list__(self):
	# 	self.Region.TestingQueue.remove(self)

	# def __getattribute__(self, item):
	# 	"""Summary
	#
	# 	Args:
	# 	    item (TYPE): Description
	#
	# 	Returns:
	# 	    TYPE: Description
	# 	"""
	# 	try:
	# 		return super(TestingState, self).__getattribute__(item)
	# 	except AttributeError:
	# 		if item in self.machine.events:
	# 			return partial(self.machine.events[item].trigger, self)
	# 		raise



class AgentStatusA(TestingState):
	"""The Statemachine of the agent"""
	status  = ['Free','Quarantined','Out_of_campus','Hospitalized','ICU','Isolation']
	# TestingState
	def __init__(self):
		"""Agent Status class is responsible for figuring out the Mobility of the agent, the agent mobility can be
		'Free','Quarantined','Out_of_campus','Hospitalized','ICU','Isolation'
		"""

		super(AgentStatusA, self).__init__()
		self.ADDED_BIT 				= True
		self.TruthStatus 			= None
		self.Last_Added_Placeholder = None
		self.buffer = []

		self.Status 				= self.status[0]

	# def log_update(self,message):

	def update_objects(self,TruthStatus):
		"""Update object of Virusmodel
		Args:
			TruthStatus (object): Truth State object to update
		"""
		self.TruthStatus 		= TruthStatus

	def __remove_from_transport__(self):
		if self.useTN == True:
			self.Region.TravellingCitizens.remove(self)

			#print('Person {} removed from travelling list of Region {}. New length = {}'.format(self.IntID, self.Region.Name, len(self.Region.TravellingCitizens)))

	def _remove_(self):
		"""Remove from workplace and transport list
		"""
		if self.ADDED_BIT:
			obj = self.get_workplace_obj(self.master)
			if obj !=None:
				self.buffer.append('_remove_')
				lock = obj.get_lock(self.master)
				lock.acquire()
				try:
					indx = list(obj.Working).index(self.IntID)
				except:
					#print(self.buffer)
					# 	#raise
					lock.release()
					self.ADDED_BIT = False
					self.__remove_from_transport__()
					return

				obj.Working[indx] = obj.Working[obj.Counter.value-1]
				obj.Counter.value -=1
				lock.release()
			self.ADDED_BIT = False

			self.__remove_from_transport__()

	def _add_(self):
		"""Add to workplace and transport list
		"""
		if ~self.ADDED_BIT:
			obj = self.get_workplace_obj(self.master)
			if obj != None:
				if obj.Working!=None:
					self.buffer.append('_add_')
					lock = obj.get_lock(self.master)
					lock.acquire()
					obj.Working[obj.Counter.value] = self.IntID
					obj.Counter.value +=1
					lock.release()
				self.ADDED_BIT = True

			if self.useTN == True:
				self.Region.TravellingCitizens.append(self)


	'''
	def _left_(self):
		"""Leave campus, calls remove
		"""
		self._remove_()

	def _entered_(self):
		"""Come back to campus
		"""
		self._add_()
	'''

	def __remove_from_placeholder__(self):
		"""Remove the person from the Truth Status Placeholders
		Returns:
			bool: Whether Removed or not
		"""
		try:
			if self.Last_Added_Placeholder == "SFree":
				self.TruthStatus.SFreeP.remove(self)

				return True

			elif self.Last_Added_Placeholder == "HQuarantined":
				self.TruthStatus.HQuarantinedP.remove(self)
				return True

			elif self.Last_Added_Placeholder == 0:  # If he is AFreeP
				self.TruthStatus.AFreeP.remove(self)

				return True
			elif self.Last_Added_Placeholder == 1:  # If he was quarantined
				self.TruthStatus.AQuarantinedP.remove(self)

				return True
			elif self.Last_Added_Placeholder == 2:  # If he was Isolated
				self.TruthStatus.SIsolatedP.remove(self)

				return True
			elif self.Last_Added_Placeholder == 3:  # If he was Hospitalized
				self.TruthStatus.SHospitalizedP.remove(self)
				return True
			elif self.Last_Added_Placeholder == 4:  # If he was Icu
				self.TruthStatus.SIcuP.remove(self)
				return True
			else:
				return False
		except:
			self.about()
			raise

	def leave_campus(self):
		acceptable_status	= [self.status[0]]
		try:
			assert self.Status in acceptable_status
		except:
			print('##########', self.Status)
			raise
		self.Status  		= self.status[2]
		self._left_()

		self.__remove_from_placeholder__()
		self.Last_Added_Placeholder = None

	def enter_campus(self):
		acceptable_status	= [self.status[2]]
		try:
			assert self.Status in acceptable_status
		except:
			print('##########', self.Status)
			raise
		self.Status  		= self.status[0]
		#self._entered_()
		if self.is_Asymptomatic():
			self.TruthStatus.AFreeP.append(self)
			self.Last_Added_Placeholder = 0

	def quarantined(self):
		acceptable_status	= [self.status[0],self.status[1],self.status[2],self.status[5]]
		assert self.Status in acceptable_status

		if self.Last_Added_Placeholder != 1:
			self.__remove_from_placeholder__()

		if self.is_Free() or self.is_Isolation():	# If free add to quarantined placeholders
			if self.State == self.states[0]:
				self.TruthStatus.HQuarantinedP.append(self)
				self.Last_Added_Placeholder = "HQuarantined"
			else:
				self.TruthStatus.AQuarantinedP.append(self)
				self.Last_Added_Placeholder = 1

		if self.Status == acceptable_status[0] or self.Status == acceptable_status[1] or self.Status == acceptable_status[3]:
			self.Isolation_Days = self.Campus.pm.Quarantine_Period
		self.Status  		= self.status[1]
		#self._remove_()
	def free_Qcentre(self):
		if self.Q_building != self.residence_building_id and self.Q_building!=-1:  # free the unit of quarantine centre
			self.Campus.sectors["Residence"].non_occupied_rooms["Student Residence"][self.Q_building].append(self.Q_unit.Id)
		self.Q_unit = -1
		self.Q_building = -1
		self.Isolation_Days = 0


	def hospitalized(self):
		acceptable_status	= [self.status[0],self.status[1],self.status[5]]
		assert self.Status in acceptable_status
		self.Status  		= self.status[3]
		#self._remove_()

		self.show_symptoms()

		if self.__remove_from_placeholder__(): #If person is in campus and removal is successful
			self.TruthStatus.SHospitalizedP.append(self)
			self.Last_Added_Placeholder = 3
		if self.Q_unit != -1:
			self.free_Qcentre()

	def admit_icu(self):
		acceptable_status	= [self.status[0],self.status[1],self.status[3],self.status[5]]
		assert self.Status in acceptable_status
		self.Status  		= self.status[4]
		#self._remove_()

		self.show_symptoms()

		if self.__remove_from_placeholder__(): #If person is in campus and removal is successful
			self.TruthStatus.SIcuP.append(self)
			self.Last_Added_Placeholder = 4
		if self.Q_building != -1:
			self.free_Qcentre()

	def isolate(self):
		acceptable_status	= [self.status[0],self.status[1],self.status[3],self.status[4],self.status[5]]
		assert self.Status in acceptable_status

		# if self.Status == self.status[0] or self.Status == self.status[1]:
		# 	self.show_symptoms()

		self.show_symptoms()

		if self.Last_Added_Placeholder != 2:
			if self.__remove_from_placeholder__(): #If person is in campus and removal is successful
				self.TruthStatus.SIsolatedP.append(self)
				self.Last_Added_Placeholder = 2

		self.Isolation_Days = self.Campus.pm.Quarantine_Period
		self.Status  	= self.status[5]
		#self._remove_()

	def free(self):
		self.Status = self.status[0]
		if self.__remove_from_placeholder__():  # If person is in campus and removal is successful
			if self.State == self.states[2]:
				self.TruthStatus.SFreeP.append(self)
				self.Last_Added_Placeholder  = "SFree"
			elif self.State == self.states[1]:
				self.TruthStatus.AFreeP.append(self)
				self.Last_Added_Placeholder = 0
		if self.Q_building != -1:
			self.free_Qcentre()


	def is_Free(self):
		return self.Status == self.status[0]
	def is_quarantined(self):
		return self.Status == self.status[1]
	def is_Out_of_Campus(self):
		return self.Status == self.status[2]
	def is_Hospitalized(self):
		return self.Status == self.status[3]
	def is_ICU(self):
		return self.Status == self.status[4]
	def is_Isolation(self):
		return self.Status == self.status[5]

class AgentStateA(AgentStatusA):
	states  = ['Healthy','Asymptomatic','Symptomatic','Recovered','Died','pseudo_symptom']

	def __init__(self):
		"""Agent status is the status of person with respect ot the virus
		"""

		super(AgentStateA, self).__init__()
		#self 				= person
		self.State 			= self.states[0]
		self.TruthStatus 	= None

	def infected(self):
		acceptable_states	= [self.states[0]]
		assert self.State in acceptable_states
		self.State  		= self.states[1]

		self.TruthStatus.AFreeP.append(self)

		self.Last_Added_Placeholder = 0

	def show_symptoms(self):
		acceptable_states	= [self.states[1],self.states[2]]
		assert self.State in acceptable_states
		self.State  		= self.states[2]

	def recover(self):
		acceptable_states	= [self.states[2]]
		assert self.State in acceptable_states
		self.State  		= self.states[3]
		self.Status   		= self.status[5]
		if self.__remove_from_placeholder__(): #Removal is succesful, mtlb seher me h
			self.TruthStatus.RRecoveredP.append(self)
			self.Last_Added_Placeholder =5
		self.in_hospital = False


	def die(self):
		acceptable_states	= [self.states[2]]
		assert self.State in acceptable_states
		self.State  		= self.states[4]
		self.Status 		= self.status[5]
		if self.__remove_from_placeholder__(): #Removal is succesful, mtlb seher me h
			self.TruthStatus.RDiedP.append(self)
			self.Last_Added_Placeholder = 6

	def is_Healthy(self):
		return self.State == self.states[0]
	def is_Asymptomatic(self):
		return self.State == self.states[1]
	def is_Symptomatic(self):
		return self.State == self.states[2]
	def is_Recovered(self):
		return self.State == self.states[3]
	def is_Died(self):
		return self.State == self.states[4]

class VaccinationStatus(object):
	"""
	Tracks the Vaccination Status of the person
	"""
	
	vaccination_states  = ["Not_Vaccinated", "Partially_Vaccinated", "Fully_Vaccinated"]

	def __init__(self):
		self.Vaccination_State = self.vaccination_states[0]

	def Gets_First_Dose(self):
		acceptable_states	= [self.vaccination_states[0]]
		assert self.Vaccination_State in acceptable_states

		self.Vaccination_State = self.vaccination_states[1]

	def Gets_Second_Dose(self):
		acceptable_states	= [self.vaccination_states[1]]
		assert self.Vaccination_State in acceptable_states

		self.Vaccination_State = self.vaccination_states[2]
