import json
import pandas as pd
import os


def process_subject(file):
    """ For creating json with subjects & slots

    Args: 
        file(str): Name of the file
    
    Returns:
        slot_dict of subjects along with their slot & rooms 
    """
    df = pd.read_csv(file)

    slot_dict = {}
    for i in df.index:
        subject = df["Subject"][i]
        slots = df["Slot"][i]

        if(type(slots)!=str):
            print(subject + " " + str(slots))

        if(type(slots)==str):
            if(slots=='--'):
                slots="NA"
            
            else:
                slots = slots.split(',')

            rooms = df["Room"][i]
            if(type(rooms)!=str):
                slot_dict[subject] = (slots,"NA")

            else:
                rooms_set = set(df["Room"][i].split(","))
                rooms_list = list(rooms_set)
                slot_dict[subject] = (slots,rooms_list)


    return slot_dict
        
def extract_data(subjects):
    """ For extracting rooms & depts list from subjects.json

    Args:
        subjects(dict): dict containing courses with their slots, rooms & strength
    """
    rooms = []
    depts = []

    for subject in subjects:
        room = subjects[subject]["room"]
        dept = subject[:2]
        
        if (dept not in depts):
            depts.append(dept)

        if (room!="NA"):
            for entry in room:
                if(entry not in rooms):
                    rooms.append(entry)
    
    depts.sort()
    rooms.sort()

    return rooms, depts


def main():
    file_path = os.getcwd()
    # file_path = os.getcwd() + "/subject_slots"
    file_list = os.listdir(file_path)

    with open(file_path + "/Schedule/slots.json") as fp:
        slots = json.load(fp)
    
    temp = []
    for entry in slots:
        temp.append(entry)
    
    print(temp)
    
    # slots_dict = {}
    # file = "ch.csv"
    # for file in file_list:
    #     dept_slots_dict = process_subject(file_path+ "/"+ file)
    #     slots_dict.update(dept_slots_dict)

    # with open("subject_slots.json",'w') as fp:
    #     json.dump(slots_dict,fp,sort_keys=True,indent=3)

    
        
if __name__ == "__main__":
    main()
