import numpy as np

from shapely.geometry import Point
from pyproj import Geod
from .utils import interperson_distance, next_perfect_square
from .contact_graph import get_susceptible_contact_dict
from .lockdown import region_Lockdown

geod = Geod(ellps="WGS84")

class Unit():
    """
    A Class for storing a unit of a Sector like a Residence, Nalanda classrooms, Department office etc.

    Args :
        Id                         : Id of Unit
        Building                   : Building to which the unit belongs (Eg. Nalanda)
        Number_Workers             : Number of staff working here
        Height                     : Floor
        x_coordinate               : Location
        y_coordinate               : Location
        Sector                     : Name of the Sector
        area                       : Area of the unit
        isclassroom                : is true when the unit is a classroom
    """
    def __init__(self,Id,Building,Number_Workers,Height,x_coordinate,y_coordinate,Sector,area,isclassroom=False,capacity=1):
        self.Id                         = Id
        self.Building                   = Building
        self.Sector                     = Sector
        self.Number_Workers             = Number_Workers
        self.height                     = Height
        self.location                   = Point(x_coordinate,y_coordinate)
        self.working                    = {}
        self.default_visiting           = {"monday": {}, "tuesday": {}, "wednesday": {}, "thursday": {}, "friday": {}, "saturday": {}, "sunday": {}}
        self.visiting                   = {}
        self.unit_contact_dict          = {}
        self.isclassroom                = isclassroom
        self.area                       = area

        if self.Sector == "Residence":
            self.capacity  = 1  # Currently hardcoded as the backend is not filling default values for capacity as 40 for all building and rooms
        else:
            self.capacity = capacity
        self.occupancy                  = 0
        self.interpersonDist            = None  #function(self.area,self.working+self.visiting)

    def fill_unit_contact_dict(self):
        """
        This function is used for filling the unit contact dictionary with the generated contacts
        """
        for i in self.visiting:
            # self.unit_contact_matrix[i] = np.zeros((len(self.visiting[i]),len(self.visiting[i])))
            self.unit_contact_dict[i] = {j:[] for j in self.visiting[i]}
        get_susceptible_contact_dict(self)

    def calc_interperson_distance(self):
        """
        This function calculates the inter person distance using the area of the unit and number of people in the unit
        """
        self.interpersonDist = {}
        for i in self.visiting:
            n = len(self.visiting[i])
            if n == 1 or n == 0:
                self.interpersonDist[i] = None
                continue
            self.interpersonDist[i] = (self.area**0.5)*(interperson_distance[str(n)])
        

#class of Buildings

class Buildings(region_Lockdown):
    """
    A Class for storing a Building like Academic building, Department building, A hostel etc.

    Args :
        pm                          : Parameters Object
        ind                         : Index of Building
        SectorName                  : Name of the sector which the building belongs
        Buildingid                  : Id of building
    """
    def __init__(self, pm, ind, SectorName, Buildingid):   # building id or building name
        super().__init__()
        self.id                          = Buildingid
        self.SectorName                  = SectorName
        self.num_rooms_per_floor         = pm.num_rooms_per_floor[ind]
        self.height                      = pm.heights[ind]
        self.location                    = [pm.xlist[ind], pm.ylist[ind]]
        self.building_area_in_sqm2       = abs(geod.geometry_area_perimeter(pm.polygons[ind])[0])
        self.buildingactivehours         = {"monday": {}, "tuesday": {}, "wednesday": {}, "thursday": {}, "friday": {}, "saturday": {}, "sunday": {}}
        #active Hours can be neglected for hostels and medical facilities or given 1 indiacating 24 hours active
        self.Number_Workers              = 0
        self.Building_units_list         = {}



class Sector(region_Lockdown):
    """
    A class for storing a sector like Academic, Residential, Hospital etc.

    Args :
        pm                          : Parameters Object
        SectorName                  : Name of the sector
    """
    def __init__(self,pm,SectorName):
        super().__init__()
        self.building_ids               = []
        self.SectorName                 = SectorName
        self.num_rooms_per_floor        = {}
        self.Number_Workers             = {}
        self.height                     = {}
        self.location                   = {}
        self.building_area              = {}
        self.Units_list                 = {}
        self.rooms_packing_fraction     = {} # denotes how much of the area of a floor is covered by all the rooms
        self.room_area                  = {}


        self.__get_building_ids__(pm)

        self.Number_Buildings                   = len(self.building_ids)

        for i in self.building_ids:
            j = pm.building_id_to_indx[i]
            self.Units_list[i]                  = {}
            self.num_rooms_per_floor[i]         = pm.num_rooms_per_floor[j]
            self.Number_Workers[i]              = pm.Number_Workers[j]
            self.height[i]                      = pm.heights[j]
            self.location[i]                    = [pm.xlist[j], pm.ylist[j]]
            self.building_area[i]               = abs(geod.geometry_area_perimeter(pm.polygons[j])[0])
            self.rooms_packing_fraction[i]      = pm.rooms_packing_fraction[j]
            self.room_area[i]                   = self.rooms_packing_fraction[i]*self.building_area[i]/self.num_rooms_per_floor[i]

    def __get_building_ids__(self, pm):
        """
        This function loads building ids  of a sector from the paramters

        Args :
            pm                          : Parameters Object
        """
        i = 0
        while i < len(pm.description):
            # print(pm.description[i],self.SectorName)
            if pm.description[i] in self.SectorName:
                self.building_ids.append(int(pm.building_ids[i]))
            i+=1

class Academic(Sector):
    """
    Class of Academic Sector

    Args :
        pm                          : Parameters Object
    """
    def __init__(self,pm):
        super().__init__(pm, ['Academic', 'Administration'])
        self.Types              = ['Classroom', 'Office']

class Residence(Sector):
    """
    Class of Residence Sector

    Args :
        pm                          : Parameters Object
    """
    def __init__(self,pm):
        super().__init__(pm, ['Student Residence', 'Faculty Residence', 'Staff Residence'])
        self.Types              = ['Student Residence', 'Faculty Residence', 'Staff Residence']
        self.non_occupied_rooms = {i: {} for i in self.Types}

    def generate_unoccupied_rooms_list(self,pm):
        """
        This function generates the unoccupied rooms list of a Residence sector which is used while intialising residence units to people
        """
        for i in self.building_ids:
            temp_description = pm.description[pm.building_id_to_indx[i]]
            if temp_description in self.Types:
                if self.non_occupied_rooms[temp_description].get(i, -1) == -1:
                    self.non_occupied_rooms[temp_description][i] = []
                self.non_occupied_rooms[temp_description][i].extend([room_id for room_id in self.Units_list[i]])
        # print(self.non_occupied_rooms)
# TO DO: All will inherit from sector

class Restaurant(Sector):
    """
    Class of Restaurant Sector and has functionalities related to it

    Args :
        pm                          : Parameters Object
    """
    def __init__(self,pm, Factor=None):
        super().__init__(pm, ['Restaurant'])
        self.Types              = ['Dine In','Take Away']
        self.Capacity           = {}
        self.Factor             = Factor

        def update_capacity(self):
            for i in range(len(self.num_rooms_per_floor)):
                self.Capacity[self.Types[i]]=self.Factor[i]*self.Sub_Class_People[i]

class Healthcare(Sector):
    """
    Class of Healthcare Sector and has functionalities related to it

    Args :
        pm                          : Parameters Object
    """
    def __init__(self, pm, Factor=None):
        super().__init__(pm, ['Healthcare'])
        self.Types              = ['Care_Center', 'Health_Center', 'Hospital']
        self.Factor             = Factor

        # TODO: Fix workaround (proper calc using ReduceFactor and TrueSecExp)
        self.Capacity           = {'Care_Center': 200,
                                    'Health_Center': 200,
                                    'Hospital': 50
                                    }

        # TODO: Add ReduceFactor
        """
        def update_capacity(self):
            for i in range(len(self.num_rooms_per_floor)):
                self.Capacity[self.Types[i]]=self.Factor[i]*self.Sub_Class_People[i]
        """

class Market(Sector):
    """
    Class of Market Sector and has functionalities related to it

    Args :
        pm                          : Parameters Object
    """
    def __init__(self,pm):
        super().__init__(pm, ['Market', 'Facility'])
        self.Types              = ['Stationary', 'Vegetable Market', 'Department Store', 'Electronics Store']

class Gymkhana(Sector):
    """
    Class of Gymkhana Sector and has functionalities related to it

    Args :
        pm                          : Parameters Object
    """
    def __init__(self,pm):
        super().__init__(pm, ['Gymkhana'])
        self.Types              = ['Indoor', 'Outdoor']
        self.Capacity={}

class Grounds(Sector):
    """
    Class of Grounds Sector and has functionalities related to it

    Args :
        pm                          : Parameters Object
    """
    def __init__(self,pm):
        super().__init__(pm, ['Grounds'])
        self.Types              = ['Sports', 'Parks']

class Non_Academic(Sector):
    """
    Class of Non_Academic Sector and has functionalities related to it

    Args :
        pm                          : Parameters Object
    """
    def __init__(self,pm):
        super().__init__(pm, ['Non_Academic'])

class Guest_House(Sector):
    """
    Class of Guest_House Sector and has functionalities related to it

    Args :
        pm                          : Parameters Object
    """
    def __init__(self,pm):
        super().__init__(pm, ['Guest House'])

class Mess(Sector):
    """
    Class of Mess Sector and has functionalities related to it

    Args :
        pm                          : Parameters Object
    """
    def __init__(self, pm):
        super().__init__(pm, ['Mess'])

if __name__ == '__main__':
    from parameters import Parameters
    pm = Parameters('shapes/kgpbuildings.shp','Campus_data/KGP Data - Sheet1.csv')
    #i = pm.BuildingInfo(BuildingName="Mechanical Engineering")['id']
    a = Sector(pm.returnParam())
    print("The Total Number of Buildings: ",a.Total_Num_Buildings)

    print(a.ParamObj.building_name[31])
    print(a.ParamObj.building_name[0])
    print(a.ParamObj.building_name[2])
    print(a.ParamObj.building_name[87])
    print(a.ParamObj.building_name[8])
    print(a.ParamObj.building_name[100])
    print(a.ParamObj.building_name[32])
   # p =[]
    #for i in range(len(a.Units_Placeholder)):
     #   p.append(plt.scatter([a.Units_Placeholder[i][k].x for k in a.Units_Placeholder[i]],[a.Units_Placeholder[i][k].y for k in a.Units_Placeholder[i]]))
    p1 = plt.scatter([a.Units_Placeholder[31][k].location.x for k in a.Units_Placeholder[31]],[a.Units_Placeholder[31][k].location.y for k in a.Units_Placeholder[31]],marker='h')
    p2 = plt.scatter([a.Units_Placeholder[0][k].location.x for k in a.Units_Placeholder[0]],[a.Units_Placeholder[0][k].location.y for k in a.Units_Placeholder[0]],marker='.')
    p3 = plt.scatter([a.Units_Placeholder[2][k].location.x for k in a.Units_Placeholder[2]],[a.Units_Placeholder[2][k].location.y for k in a.Units_Placeholder[2]],marker='*')
    p4 = plt.scatter([a.Units_Placeholder[87][k].location.x for k in a.Units_Placeholder[87]],[a.Units_Placeholder[87][k].location.y for k in a.Units_Placeholder[87]],marker='s')
    p5 = plt.scatter([a.Units_Placeholder[8][k].location.x for k in a.Units_Placeholder[8]],[a.Units_Placeholder[8][k].location.y for k in a.Units_Placeholder[8]],marker='v')
    p6 = plt.scatter([a.Units_Placeholder[100][k].location.x for k in a.Units_Placeholder[100]],[a.Units_Placeholder[100][k].location.y for k in a.Units_Placeholder[100]],marker='x')
    p7 = plt.scatter([a.Units_Placeholder[32][k].location.x for k in a.Units_Placeholder[32]],[a.Units_Placeholder[32][k].location.y for k in a.Units_Placeholder[32]],marker="+")
    plt.axis('square')
    plt.show()

    #print("The Mechanical Engineering Building has rooms with following (ids,visitors) :",[(k,a.Units_Placeholder[i][k].visiting) for k in a.Units_Placeholder[i].keys()])
    #print(pm.BuildingInfo(BuildingName="Mechanical Engineering"))
    #print(a.Index_Holder)
