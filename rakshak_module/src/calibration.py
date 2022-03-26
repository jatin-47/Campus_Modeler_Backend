import numpy as np 
import math 
import statistics
import json


# Applicable for entire city
def distance_dist(pm, distance, Dist=None):
	'''
	This function represents Distance wise Absoulte Risk Distribution of the corona virus 
	Inputs: 
	distance: float 
	Dist 	: dict having constant and ratio keys (optional)
	
	returns
	absolute risk: float 

	abs_risk = Constant / (distance*Ratio)
	Constant = Value of absolute risk < 1 m 
	Ratio  	 = Per m decrease in Risk
	'''
	if Dist is None:
		Param = pm.Virus_DistanceDist.copy()
	else:
		Param = Dist

	if distance<1:
		return Param["Constant"]
	else:
		# return Param["Constant"]/(distance*Param["Ratio"])
		return Param["Constant"]/(Param["Ratio"]**(distance-1))

# Applicable for entire city
def effective_contact_rate(time, d, const, pm):
	'''
	Effective Contact Rate is calculated as follows
	Beta(ECR) = gamma x p 
	gamma = total contacts = exposure time in hours x contacts per hour
	p 	  = probablity of tranmission per contact = absoulte risk(distance)
	'''
	def gamma(time,contacts_ph):
		return time*contacts_ph
	def p(distance):
		return distance_dist(pm, distance)
	return const*(1-(1-p(d))**time)

def effective_contact_rate_new(gamma, avg_interperson_distance, avg_exp_time, pm, virus_c=1):
	"""
	Effective Contact Rate is calculated as follows
	Beta(ECR) = gamma x p
	gamma = total contact rate = expected number of total contacts for a person per unit time in that interaction space
	p 	  = probability of transmission per contact = virus_c x (1-(1-risk(avg_interperson_dist))^(avg_exposure_time))
	risk(d) = probability of transmission of virus if the the susceptible agent is at distance d for unit time
	"""
	def p(distance, time):
		return virus_c*(1-(1-distance_dist(pm, distance))**time)
	return gamma*p(avg_interperson_distance, avg_exp_time)

def get_TR(pm,c=1):
	"""returns the TR of different interaction spaces

	Args:
		c (int, optional): 	Constant value of virus. Defaults to 1.
		pm (parameters object): Parameters object.

	Returns:
		TR: Transmission Rate of different interaction spaces
	"""	

	Virus_Params 		= pm.Virus_Params.copy()
	Mask_Fraction 		= pm.Sector_Mask_Fraction.copy() # Fraction of the people in each sector who wear a mask.


	sectors = ['Home','Transport','Grocery','Unemployed','Random']
	TR 				= {}
	for sector in sectors:
		TR[sector] = effective_contact_rate(Virus_Params[sector]['Time'],Virus_Params[sector]['Distance']*Mask_Fraction[sector],c,pm)
	
	return TR

# Applicable for entire city
def sector_proportions(pm, sector=None):
	'''
	sector Proportions(SP) is the Expected proportion of people employed in Different Sectors
	SP 		= sum(AgeDist[x]*Employment[x]) at y axis
	for all x in ageGroups
	'''
	sectors 		= pm.sectors.copy()
	AgeDist 		= pm.Population_Dist.copy()
	AgeGroups 		= pm.Population_groups.copy()
	ProblityPurchase = pm.Transaction_ProbablityOfPurchase
	Family_size 	= pm.Family_size.copy()[0]

	Prob_use_tran 	= pm.Prob_use_TN

	#TODO: Unemployed value is given zero have to change
	proportions = {'Home':1,'Transport':Prob_use_tran,'Grocery':ProblityPurchase/Family_size,'Unemployed': 0,'Random':1}

	proportions.update({
			'Education'	: 0.6,
			'Office'	: 0.1,
			'Commerce'	: 0.1,
			'Healthcare': 0.1})
	
	if sector is None:
		return proportions
	else:
		return proportions[sector]

# Applicable for City/Region Wise
def sectors_susceptible(pm, sector=None, RegionName=None):
	'''
	returns the proportion of people susceptible in each sector when the entire population is working in that sector
	i.e susceptible population when exactly 1 person works in that sector 
	eg
	P=100  	: people working in sector X
	susp=0.2: returned by this function for sector X
	then for each person in sector X suspected population is P x susp = 20  
	For home, Unemployed, the value is fixed at family size as it is not dependent on total population
	For random it is equal to 4*pi*D*(P/4*pi*D)^cr, where D is density, P is the area population and cr is the compliance Rate ranging between 0 and 1
	'''
	# For entire Campus
	Family_size 	= pm.Family_size.copy()[0]
	Total_Pop 		= pm.Population
	AvgDensity		= Total_Pop/pm.Total_area # people per m^2


	CR0					= pm.Initial_Compliance_Rate 
	TN_use_probablity 	= pm.Prob_use_TN
	Total_Buses			= pm.NumBuses

	susceptibles        = {'Home':Family_size}

	susceptibles.update({
			'Education'	: 0.05,
			'Office'	: 0.1,
			'Commerce'	: 0.1,
			'Healthcare': 0.1})


	#TODO : Check Math later

	# susceptibles['Grocery'] 	= (susceptibles['Commerce']+1.0/(Family_size*sum(Workplace_Params["Commerce_NumberOfSizei"]))) #TODO:update later
	susceptibles['Grocery'] 	= 0
	susceptibles['Unemployed'] 	= sector_proportions(pm,sector='Unemployed')*Family_size #UPDATE LATER
	susceptibles['Transport'] 	= TN_use_probablity/Total_Buses
	
	Const 						= 4*math.pi*AvgDensity
	susceptibles['Random'] 		= Const*((Total_Pop/Const)**(1-CR0))
	return susceptibles
		
# def R0(pm, c=1):
# 	'''
# 	returns R0 value of the given campus
# 	R0perday = Sum_i P(pop_i) x effective_contact_rate x Suspected_i
# 	where i is the Place of transmission,
# 	P(pop_i)  	: Proportion of people experiancing i
# 	Suspected_i	: Suspected people at i
# 	R0 		= R0perday x ExpectedIncubationPeriod
# 	'''
# 	Virus_Params 	= pm.Virus_Params.copy()
# 	Population 		= pm.Population
# 	Incubation_Per  = pm.Virus_IncubationPeriod
# 	AgeDist 		= pm.Population_Dist
# 	susceptibles 	= sectors_susceptible(pm=pm)
# 	proportions 	= sector_proportions(pm=pm)
#
#
# 	sectors = ['Education','Office','Commerce','Healthcare','Home','Transport','Grocery','Unemployed','Random']
# 	Rperday 		= 0
# 	Rsector = {}
# 	printdata = []
# 	for sector in sectors:
# 		ecr = effective_contact_rate(Virus_Params[sector]['Time'],Virus_Params[sector]['Distance'],c,pm)
# 		pop =(proportions[sector])
# 		if sector in ['Home','Unemployed','Random']:
# 			susp=(susceptibles[sector])
# 		else:
# 			susp=(susceptibles[sector]*Population*pop)
#
# 		Rsector[sector] = ecr*pop*susp
#
# 		Rperday += Rsector[sector]
# 		printdata.append([sector+":",np.round(ecr,decimals=2),np.round(pop,decimals=2),np.round(susp,decimals=2),np.round(Rsector[sector],decimals=2)])
#
# 	EDays 	= np.average(Incubation_Per,weights=AgeDist)
# 	R0 		= Rperday*EDays
# 	print(tabulate(printdata,headers=["Sector","EffContRate","Population","susceptibles","Rate of sector"]))
# 	print("Calculated R0: ", R0)
# 	return R0
'''
def R0_new(pm):
	"""Calculates R0 for the movements generated using the data_IITKGP obtained from the simulation"""
	Population			= pm.Population
	IncubationPeriod	= pm.Virus_IncubationPeriod.copy()
	AgeDist 		= pm.Population_Dist
	with open('total_interaction_time.json', 'r') as fh:
		data_IITKGP = json.load(fh)
	Rsum = 0
	for building in data_IITKGP:
		for unit in data_IITKGP[building]:
			distance = data_IITKGP[building][unit]["avg_interperson_distance"]
			if type(distance) != float:
				continue
			try:
				# temp=effective_contact_rate_new(data_IITKGP[building][unit]["gamma"],distance,data_IITKGP[building][unit]["avg_exp_time"],pm)*data_IITKGP[building][unit]["avg_people_visiting"]
				Rsum+=data_IITKGP[building][unit]["R0"]
				# if temp!=0:
				# 	print(data_IITKGP[building][unit]["gamma"]*(1-(1-distance_dist(pm,distance))**data_IITKGP[building][unit]["avg_exp_time"]),data_IITKGP[building][unit]["avg_people_visiting"]/Population)
			except:
				pass
	EDays 	= np.average(IncubationPeriod,weights=AgeDist)
	Rsum /= Population
	print("Calculated R0 using the simulated movements = {} (taking c=1)".format(Rsum*EDays))

	return Rsum*EDays
'''

def calibrate(pm,R0_val=None):
	if R0_val is None:
		R0_val = pm.Virus_R0 
	Current_R0 = R0(pm=pm)

	c = R0_val/Current_R0
	return c

# def calibrate_new(pm,R0_val=None):
# 	if R0_valis None:
# 		R0_val = pm.Virus_R0
# 	Current_R0 = R0_new(pm=pm)
#
# 	c = R0_val/Current_R0
# 	return c
