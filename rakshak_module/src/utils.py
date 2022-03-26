import os
import json
import time
import random
import datetime
import pandas as pd
import numpy as np
import math

from .contact_graph import get_susceptible_contact_matrix
from .calibration import distance_dist

with open("rakshak/utilities/interperson_dist.json", 'r') as fh:
    interperson_distance = json.load(fh)     # loads the data_IITKGP which has been obtained from "http://hydra.nat.uni-magdeburg.de/packing/csq/csq.html#overview"

def func_timer(func):
    def inner(self,**kwargs):
        if self.pm.Verbose:
            start = time.time()
            func(self,**kwargs)
            end = time.time()
            print("{} takes {} sec".format(str(func.__name__), end - start))
        else:
            func(self,**kwargs)

    return inner

def total_students(course, grades, grades_18A, grades_18S, na_list):
    """Gives the count of total students present in the course
        by adding all the grade allocations.

    Args:
        course (str): Course code
        grades,grades_18A,grades_18S (dict): Course Grade Report
        na_list (list): A list of the subjects with name (wherever possible)
                        whose strength couldn't be determined.

    Returns:
        strength (int): Strngth of the course.
    """
    strength = 0
    try:
        course_grades = grades[course]["grades"]

        print(course + " grades found")
        for grade in course_grades:
            print(course_grades[grade])
            strength = strength + course_grades[grade]

        return strength

    except KeyError:
        if course in grades_18A:
            course_grades = grades_18A[course]["grades"]

            print(course + " grades found")
            for grade in course_grades:
                print(course_grades[grade])
                strength = strength + course_grades[grade]

            return strength
        elif course in grades_18S:
            course_grades = grades_18S[course]["grades"]

            print(course + " grades found")
            for grade in course_grades:
                print(course_grades[grade])
                strength = strength + course_grades[grade]

            return strength
        else:
            try:
                txt = course + "- " + grades[course]["name"]
                if txt not in na_list:
                    na_list.append(txt)
            except KeyError:
                if course not in na_list:
                    na_list.append(course)

            print(course + " grades not found")
            return "NA"


def gen_timetable(file_path, schedule, grades, grades_18A, grades_18S):
    """Generates timetable through chill-zone + Kronos Json Files

    Args:
        file_path (str): path where the json are present.
        schedule (dict): Day-Wise course occupancy of the rooms
        grades,grades_18A,grades_18S (dict): Course Grade Report

    Returns:
        na_list (list): A list of the subjects with name (wherever possible)
                        whose strength couldn't be determined.

    Writes:
        occupancy.json: With strengths present in different rooms at
                        different times of the day.
    """
    na_list = []
    room_dict = {}
    for room in schedule:
        occupancy = schedule[room]
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        timmings = ['8-9','9-10','10-11','11-12','12-13','14-15','16,17','17-18']
        day_dict = {}
        for i in range(5):
            day = occupancy[i]
            stsrengths = {}
            for j in range(8):
                course  = day[j]
                if course != "":
                    print(course + " initiated")
                    strengths[timmings[j]] = (total_students(course, grades, grades_18A, grades_18S, na_list), course)
                else:
                    strengths[timmings[j]] = 0

            day_dict[days[i]] = strengths
        room_dict[room] = day_dict

    with open(file_path + "/occupancy_3.json", 'w') as fp:
        json.dump(room_dict, fp, sort_keys=True, indent=3)

    for entry in na_list:
        print(entry)

    return na_list

def form_subjects_real(file_path, subjects, grades, grades_18A, grades_18S):
    na_list = []
    final_subjects = {}

    for subject in subjects:
        temp = {}
        temp["strength"] = total_students(subject, grades, grades_18A, grades_18S, na_list)
        temp["slots"] = subjects[subject][0]
        temp['room'] = subjects[subject][1]
        final_subjects[subject] = temp

    with open(file_path + "/subjects.json",'w') as fp:
        json.dump(final_subjects, fp, sort_keys=True, indent=3)

    return na_list

def is_valid(subject):
    """ Checks whether the subject has sufficient information to be added to the
    """
    if(subject["strength"]=="NA"):
        return False

    return True

def is_clash(slot,lab_slots):
    """ Checks for clash of slot with
    """
    clash   = {'Q-Lab' : ['C3','B3','D3','D4'], "J-Lab" : ['H3','U3','U4'], "K-Lab" : ['D2','D3','D3','A3'], "L-Lab" : ['H2','H3','U3','U4'], "R-Lab" : ['F3','F4','G3','E3','E4'], "X-Lab" : ['X4'], "M-Lab" : ['C4','E3','E4','G3'], "N-Lab" : ['I2','V3','V3','V4'], "O-Lab" : ['E2','E4','F4','F3'], "P-Lab" : ['V4','V3','I2']}

    for entry in lab_slots:
        if(slot in clash[entry]):
            return True

    return False

def form_schedule(file_path=None,save=False):
    """ For generating shcedule for various departments

    Args:
        file_path(str): For storing the schedule.json
        save(bool): Whether to store the schedule
    """

    depts   = ['AE', 'AG', 'AR', 'BT', 'CE', 'CH', 'CS', 'CY', 'EC', 'EE', 'EX', 'GG', 'HS', 'IE', 'IM', 'MA', 'ME', 'MF', 'MI', 'MT', 'NA', 'PH', 'QE', 'QM']
    rooms   = ['NC131', 'NC132', 'NC141', 'NC142', 'NC231', 'NC232', 'NC233', 'NC234', 'NC241', 'NC242', 'NC243', 'NC244', 'NC331', 'NC332', 'NC333', 'NC334', 'NC341', 'NC342', 'NC343', 'NC344', 'NC431', 'NC432', 'NC433', 'NC434', 'NC441', 'NC442', 'NC443', 'NC444', 'NR121', 'NR122', 'NR123', 'NR124', 'NR221', 'NR222', 'NR223', 'NR224', 'NR321', 'NR322', 'NR323', 'NR324', 'NR421', 'NR422', 'NR423', 'NR424', 'S-123', 'S-125', 'S-126', 'S-127', 'S-136', 'S-216', 'S-122A', 'S-301', 'S-302', 'V1', 'V2', 'V3', 'V4']
    slots_class   = ['A3', 'B3', 'C3', 'C4', 'D3', 'D4', 'E3', 'E4', 'F3', 'F4', 'G3', 'H3', 'S3', 'U3', 'U4', 'V3', 'V4', 'X4']
    slots_lab = ['J-Lab', 'K-Lab', 'L-Lab', 'M-Lab', 'N-Lab', 'O-Lab', 'P-Lab', 'Q-Lab', 'R-Lab', 'X-Lab']


    occupied = []
    schedule = {}

    for dept in depts:

        for i in range(2,5):
            temp_dict = {}
            year_schedule = {}
            lab_slot_taken = []
            occupied_slots = []

            # Allotting Lab Courses
            for j in range(1,random.randrange(4,6)):
                room    = dept + str(i) +  "L" + str(j)
                slot    = random.choice(slots_lab)

                while(slot in lab_slot_taken):
                    #room    = random.choice(rooms)
                    slot    = random.choice(slots_lab)
                else:
                    occupied_slots.append(slot)
                    lab_slot_taken.append(slot)
                    year_schedule[room] = {"slot" : slot, "room" : room}

            # Allotting Theory Courses
            for j in range(1,random.randrange(5,8)):
                room    = random.choice(rooms)
                slot    = random.choice(slots_class)

                ctr = 0
                while((slot in occupied_slots) and ((room + "_" + slot) in occupied) and is_clash(slot,lab_slot_taken) and ctr<50):
                    room    = random.choice(rooms)
                    slot    = random.choice(slots_class)
                    ctr = ctr+1
                else:
                    if(ctr>50):
                        while((slot in occupied_slots) or is_clash(slot,lab_slot_taken)):
                            slot = random.choice(slots_class)

                        else:
                            room = dept + "-room-" + str(j)
                            occupied.append(room + "_" + slot)
                            year_schedule[dept+ str(i) + "0" + str(j)] = {"slot" : slot, "room" : room}
                    else:
                        occupied.append(room + "_" + slot)
                        occupied_slots.append(slot)
                        year_schedule[dept + str(i) + "0" + str(j)] = {"slot" : slot, "room" : room}



            if(dept in schedule):
                schedule[dept].update({i:year_schedule})

            else:
                temp_dict[i] = year_schedule
                schedule[dept] = temp_dict

    return schedule


def select_courses(strength, dist):
    """
    function to select courses for students
    """
    schedule = []
    optional_courses = []
    for key in dist:
        if int(dist[key]) > 0.6 * strength:  # Compulsory courses
            schedule.append(key)
        elif int(dist[key]) >= 0.3 * strength:
            optional_courses.append(key)

    if len(optional_courses) != 0:
        schedule.append(random.choice(optional_courses))
    return schedule


def next_perfect_square(number):
    sqroot = int(number**0.5)
    if sqroot**2 == number:
        return number
    else:
        return (sqroot+1)**2


'''
def calculate_tot_interaction_time_distance(k, day, Units_Placeholder,all_people,contact_matrix):
    """ Used to write into a file the details of no of susceptible contacts and average interperson distance in that unit everyday
    Args:
        k: dict to be updated with new day's info
        day: the day number (eg."1","2")
        Units_Placeholder: dict containing ultimately all unit objects
    Returns:
        None
    """
    # k = {}
    k[day] = {}

    for building_id in Units_Placeholder:
        k[day][building_id] = {}
        for unit_id in Units_Placeholder[building_id]:
            k[day][building_id][unit_id] = {"gamma":0,
                                            "num_people_visiting":0,
                                            "interperson_distance_cumulative":None,
                                            "no_of_times":0,
                                            "avg_exp_time":0,
                                            "R0": 0}
            Units_Placeholder[building_id][unit_id].calc_interperson_distance()
            # get_susceptible_contact_matrix(contact_matrix,Units_Placeholder[building_id][unit_id]
            temp_num_contacts = []
            avg_exp_time = {}
            for t in Units_Placeholder[building_id][unit_id].visiting:
                # xi = np.pi*(1.8288**2)/Units_Placeholder[building_id][unit_id].area
                # k[day][building_id][unit_id]["gamma"] += int(xi*len(Units_Placeholder[building_id][unit_id].visiting[t]))
                for i in Units_Placeholder[building_id][unit_id].unit_contact_dict[t]:
                    avg_exp_time[i] = avg_exp_time.get(i,0)+1
                    temp_num_contacts.append(len(Units_Placeholder[building_id][unit_id].unit_contact_dict[t][i]))
                # temp_num_contacts.extend([len(i) for i in list(Units_Placeholder[building_id][unit_id].unit_contact_dict[t].values())])
                if k[day][building_id][unit_id]["interperson_distance_cumulative"] is None:
                    k[day][building_id][unit_id]["interperson_distance_cumulative"] = 0
                if Units_Placeholder[building_id][unit_id].interpersonDist[t] is None:
                    continue
                # print(k[day][building_id][unit_id][1])
                # k[day][building_id][unit_id]["num_people_visiting"] += len(Units_Placeholder[building_id][unit_id].visiting[t])
                k[day][building_id][unit_id]["interperson_distance_cumulative"] += Units_Placeholder[building_id][unit_id].interpersonDist[t]
                k[day][building_id][unit_id]["no_of_times"] += 1
            k[day][building_id][unit_id]["num_people_visiting"] = len(avg_exp_time)
            if len(temp_num_contacts):
                if np.mean(temp_num_contacts):
                    k[day][building_id][unit_id]["gamma"] = np.mean(temp_num_contacts)

            if k[day][building_id][unit_id]["no_of_times"] != 0:
                k[day][building_id][unit_id]["avg_interperson_distance"] = k[day][building_id][unit_id]["interperson_distance_cumulative"]/k[day][building_id][unit_id]["no_of_times"]
                k[day][building_id][unit_id]["num_people_visiting"] /= k[day][building_id][unit_id]["no_of_times"]
            else:
                k[day][building_id][unit_id]["avg_interperson_distance"] = 0

            if len(avg_exp_time):   k[day][building_id][unit_id]["avg_exp_time"] = np.mean(list(avg_exp_time.values()))
            else:                   k[day][building_id][unit_id]["avg_exp_time"] = 0
            k[day][building_id][unit_id]["R0"] = k[day][building_id][unit_id]["gamma"]*(1-(1-distance_dist(pm,k[day][building_id][unit_id]["avg_interperson_distance"]))**k[day][building_id][unit_id]["avg_exp_time"])*k[day][building_id][unit_id]["num_people_visiting"]

    if day == duration:
        new = {}
        for day in k:
            # print(k[day][5][2])
            for building in k[day]:
                new[building] = {}
                for unit in k[day][building]:
                    try:
                        new[building][unit] =  {"gamma": sum([k[j][building][unit]["gamma"] for j in k])/len(k),"avg_exp_time":sum([k[j][building][unit]["avg_exp_time"] for j in k])/len(k),"avg_interperson_distance":sum([k[j][building][unit]["avg_interperson_distance"] for j in k])/len(k),"avg_people_visiting": sum([k[j][building][unit]["num_people_visiting"] for j in k])/len(k)}
                        new[building][unit]["R0"] = sum([k[j][building][unit]["R0"] for j in k])/len(k)
                    except:
                        assert 1 == 0
        with open('total_interaction_time.json', 'w') as fh:
            json.dump(new,fh,indent=3)
            # json.dump(k,fh,indent=3)
    else:
        # with open('total_interaction_time.json', 'r') as fh:
        #     old_k = json.load(fh)
        # old_k.update(k)
        pass

def c_calculate(IncubationPeriod=[6,6,8,5,2,2],AgeDist=[0,0,1482,189,0,0],Virus_DistanceDist={"Constant": 0.128, "Ratio": 2.02},Virus_R0=2.0,Population_size=None):
    c = 0
    with open('total_interaction_time.json', 'r') as fh:
        d = json.load(fh)
    sum = 0
    for building in d:
        for unit in d[building]:
            distance = d[building][unit]["avg_interperson_distance"]
            if type(distance) != float:
                continue
            if distance<1:
                D= Virus_DistanceDist["Constant"]
            else:
                D= Virus_DistanceDist["Constant"]/(Virus_DistanceDist["Ratio"]**(distance-1))
                # D= Virus_DistanceDist["Constant"]/(Virus_DistanceDist["Ratio"]*distance)
                # print(D,distance)
            try:
                sum+=d[building][unit]["gamma"]*(1-(1-D)**d[building][unit]["avg_exp_time"])*d[building][unit]["avg_people_visiting"]
            except:
                pass
    EDays 	= np.average(IncubationPeriod,weights=AgeDist)
    # print(EDays)
    # ContagiousDays_presymptomatic = 2.5
    # ContagiousDays_asymptomatic = 7
    # percent_asymptomatic = 0.2
    # Infectiousness_of_asymp_relative_to_symp = 1
    # EDays_new = ContagiousDays_presymptomatic*(1-percent_asymptomatic)+ContagiousDays_asymptomatic*percent_asymptomatic*Infectiousness_of_asymp_relative_to_symp
    # print(EDays_new)
    sum /= Population_size
    # print(sum,5.34+1.69)
    print("Calculated R0 = {} (taking c=1)".format(sum*EDays))

    return sum*EDays
'''

def random_susceptibles(Density:float,Population:int,ComplianceRate:float):
    """random_susceptibles Returns the number of Suspectile people for random Transmission
	Args:
		Density (float): density of the population
		Population (int): count of population
		ComplianceRate (float): Rate at which people obey orders, i.e entropy. Ranges between 0 to 1
	Returns:
		int: Number of susceptible people
	"""
    Const 			= 4*math.pi*Density
    if Const==0:
        return 0
    susceptibles 	= Const*((Population/Const)**(1-ComplianceRate))
    return int(np.round(susceptibles))

def main():
    # Can be set to wherever the json files are present
    file_path = os.getcwd() + "/Timetable"

    with open(file_path + "/Schedule/schedule.json", 'r',encoding='utf8') as fp:
        schedule = json.load(fp)

    with open(file_path + "/Grades/courses.json", 'r',encoding='utf8') as fp:
        grades = json.load(fp)

    with open(file_path + "/Grades/2018Autumn.json", 'r',encoding='utf8') as fp:
        grades_18A = json.load(fp)

    with open(file_path + "/Grades/2018Spring.json", 'r',encoding='utf8') as fp:
        grades_18S = json.load(fp)

    with open(file_path + "/subjects.json",'r',encoding='utf8') as fp:
        subjects = json.load(fp)

    with open(file_path + "/Schedule/slots.json",'r',encoding='utf8') as fp:
        slots = json.load(fp)

    schedule = form_schedule(file_path)
    print(schedule)

    # na_list = form_subjects_real(file_path, subjects, grades, grades_18A, grades_18S)
    # na_list = gen_timetable(file_path, schedule, grades, grades_18A, grades_18S)

    # with open(file_path + "/na_subjects_list.txt",'w') as fp:
    #     for entry in na_list:
    #         fp.write(entry + "\n")


if __name__ == "__main__":
    #main()
#    dbname, pwd = create_db_publish_locations()
#    print(dbname,pwd)


#####################   to create post class hour movements from survey data_IITKGP     ####################
    # import pandas as pd
    #
    # df = pd.read_csv("../data_IITKGP/survey_data/CAMPUS RAKSHAK (students).csv")
    #
    # df_req = df.loc[((df['Your academic program'] == 'PG') | (df['Current Year of study'] != '1st'))]
    #
    # print(df_req)
    #
    # df_req.to_csv("../data_IITKGP/survey_data/Student Choices.csv")



    # import csv
    #
    # with open('../data_IITKGP/survey_data/building_name_to_id_mapping.csv', 'r',encoding="utf8") as file:
    #     reader2 = csv.reader(file)
    #     k=0
    #     x={}
    #     hall_weights={}
    #     year_weights={}
    #     for i in range(113):
    #         hall_weights[i]={'weekdays' :{},'weekends' : {}}
    #     for i in range(1,6):
    #         year_weights[i]={'weekdays' :{},'weekends' : {}}
    #     for row in reader2:
    #         x[row[0]] = int(row[1])
    #         """
    #         for i in range(113):
    #             hall_weights[i]['weekdays'][int(row[1])] = 0
    #             hall_weights[i]['weekends'][int(row[1])] = 0
    #         for i in range(1,6):
    #             year_weights[i]['weekdays'][int(row[1])] = 0
    #             year_weights[i]['weekends'][int(row[1])] = 0
    #         """
    #         k+=1
    # for i in range(113):
    #     for j in range(113):
    #         hall_weights[i]['weekdays'][j] = 0
    #         hall_weights[i]['weekends'][j] = 0
    #     hall_weights[i]['weekdays']["Other Hall of Residence"] = 0
    #     hall_weights[i]['weekdays']["A Department"] = 0
    #     hall_weights[i]['weekends']["Other Hall of Residence"] = 0
    #     hall_weights[i]['weekends']["A Department"] = 0
    # for i in range(1,6):
    #     for j in range(113):
    #         year_weights[i]['weekdays'][j] = 0
    #         year_weights[i]['weekends'][j] = 0
    #     year_weights[i]['weekdays']["Other Hall of Residence"] = 0
    #     year_weights[i]['weekdays']["A Department"] = 0
    #     year_weights[i]['weekends']["Other Hall of Residence"] = 0
    #     year_weights[i]['weekends']["A Department"] = 0
    # print(x['Tata Sports Complex'])
    # with open('../data_IITKGP/survey_data/Student Choices.csv', 'r',encoding="utf8") as file:
    #     reader = csv.reader(file)
    #     k=0
    #     no_people_hall ={}
    #     no_people_year ={}
    #     for i in range(113):
    #         no_people_hall[i]=0
    #     for i in range(1,6):
    #         no_people_year[i]=0
    #     for row in reader:
    #         if(k==0):
    #             k+=1
    #             continue
    #         if row[15] == 'Other':
    #             k+=1
    #             continue
    #         no_people_hall[x[row[15]]]+=1
    #         no_people_year[int(row[14][0])]+=1
    #         lista = row[6].split(';')
    #         for j in lista:
    #             if j == 'Other Hall of Residence':
    #                 hall_weights[x[row[15]]]['weekdays'][j]+=1
    #                 year_weights[int(row[14][0])]['weekdays'][j]+=1
    #                 continue
    #             elif j == 'A Department':
    #                 hall_weights[x[row[15]]]['weekdays'][j]+=1
    #                 year_weights[int(row[14][0])]['weekdays'][j]+=1
    #                 continue
    #             elif j == 'Nalanda':
    #                 continue
    #             elif x[j]==-1 :
    #                 continue
    #             hall_weights[x[row[15]]]['weekdays'][x[j]]+=1
    #             year_weights[int(row[14][0])]['weekdays'][x[j]]+=1
    #         listb = row[11].split(';')
    #         for j in listb:
    #             if j == 'Other Hall of Residence':
    #                 hall_weights[x[row[15]]]['weekends'][j]+=1
    #                 year_weights[int(row[14][0])]['weekends'][j]+=1
    #                 continue
    #             elif j == 'A Department':
    #                 hall_weights[x[row[15]]]['weekends'][j]+=1
    #                 year_weights[int(row[14][0])]['weekends'][j]+=1
    #                 continue
    #             elif x[j]==-1 :
    #                 continue
    #             hall_weights[x[row[15]]]['weekends'][x[j]]+=1
    #             year_weights[int(row[14][0])]['weekends'][x[j]]+=1
    #         listc = row[9].split(';')
    #         for j in listc:
    #             if x[j]==-1 :
    #                 continue
    #             hall_weights[x[row[15]]]['weekdays'][x[j]]+=1
    #             year_weights[int(row[14][0])]['weekdays'][x[j]]+=1
    #             hall_weights[x[row[15]]]['weekends'][x[j]]+=1
    #             year_weights[int(row[14][0])]['weekends'][x[j]]+=1
    #
    #         #print(k,lista,listb)
    #         k+=1
    #     for a in hall_weights:
    #         if no_people_hall[a]==0:
    #             continue
    #         for i in hall_weights[a]['weekdays']:
    #             hall_weights[a]['weekdays'][i] = hall_weights[a]['weekdays'][i]/no_people_hall[a]
    #         for i in hall_weights[a]['weekends']:
    #             hall_weights[a]['weekends'][i] = hall_weights[a]['weekends'][i]/no_people_hall[a]
    #
    #     for a in year_weights:
    #         if no_people_year[a]==0:
    #             continue
    #         for i in year_weights[a]['weekdays']:
    #             year_weights[a]['weekdays'][i] = year_weights[a]['weekdays'][i]/no_people_year[a]
    #         for i in hall_weights[a]['weekends']:
    #             year_weights[a]['weekends'][i] = year_weights[a]['weekends'][i]/no_people_year[a]
    # print(hall_weights)
    # print(year_weights)
    # with open("../data_IITKGP/survey_data/hall_wise_place_weights.json", 'w') as fh:
    #     json.dump(hall_weights,fh, indent=3)
    # with open("../data_IITKGP/survey_data/year_wise_place_weights.json", 'w') as fh:
    #     json.dump(year_weights,fh, indent=3)


    c_calculate()





    pass

