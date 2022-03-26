import time

import src
import sys
import json
import argparse
from pymongo import MongoClient

def main():
	with open("rakshak/utilities/default_params.json", 'r') as fp:
		default_policy_input =	json.dumps(json.load(fp))


	parser = argparse.ArgumentParser()
	parser.add_argument('Campus_Name', type=str, default="IIT Jodhpur", nargs='?')
	parser.add_argument('Policy_Input', type=str, default=default_policy_input, nargs='?')
	parser.add_argument('result_path', type=str, default="results", nargs='?')

	args = parser.parse_args()

	campusname = args.Campus_Name
	policy_input = json.loads(args.Policy_Input)
	save_results_path = args.result_path

	params = {
				"Campus": campusname,
				"SIM_DAYS": policy_input["General Input"]["No of Days to Simulate"],
			  	"SimName": policy_input.get("Simulation_Name",time.strftime("%d%b%Y_%H%M%S",time.localtime())) ,
			 }

	params["Result Resolution by hours"] = policy_input["General Input"]["Result Resolution by hours"]

	params["Virus_R0"] = policy_input["Epidemic Parameter Input"]["Virus R0"]
	params["outside_infection_prob"] = policy_input["Epidemic Parameter Input"]["City Prevalence Rate"]
	params["init_case_statistics"] ={
										'Asymptomatic': policy_input["Epidemic Parameter Input"]["No of Initial Infected People"],
										'Symptomatic': 0,
										'Recovered': 0,
										'Partially_Vaccinated': 0,
										'Fully_Vaccinated': 0
									}
	params["Daily_Visitors"] = policy_input["Policy Input"]["Expected No of Visitors per Day (Other than Staff)"]
	params["Compliance Rate"] = policy_input["Policy Input"]["Compliance Rate"]
	params["Quarantine_Period"] = policy_input["Policy Input"]["Quarantine Period"]
	params["Lockdown_Areas"] = policy_input["Policy Input"]["Sector/Building to Lockdown"]


	params["SaveMovementSnapshots"] = True
	params["Vaccination_Paradigm"]  = "Random_Sampling"
	params['retesting_negative_people'] =				True
	params['retesting_positive_people_14_days_back'] =	False
	params['selecting_random_people']      = 			True
	params['selecting_retest_random_people'] = True
	params["Testing_Strategy"] = policy_input["Testing Strategy"]["Testing Strategy"]
	params["Test_sample_start_day"] = 1
	params["Testing_capacity"] = policy_input["Testing Strategy"]["Testing Capacity Per Day"]
	params["Testing_days"] = policy_input["Testing Strategy"]["Day(s) of Testing"]
	params["Test_Sensitivity"] = policy_input["Testing Strategy"]["Test Sensitivity"]
	params["Test_Specificity"] = policy_input["Testing Strategy"]["Test Specificity"]

	params["is_calibrated"] = True
	params["Dorfman_Pooling"] = False

	params["MongoClient"] = MongoClient("mongodb+srv://new-user_1:PNrHr6KD2pLvn5oR@cluster0.mzlkc.mongodb.net")
	print("Connected to DataBase")

	params["results_path"] = save_results_path
	pm = src.Parameters(**params)
	src.StartSimulation(pm=pm)

if __name__ == '__main__':

	main()

