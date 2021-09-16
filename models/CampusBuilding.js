const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');

//RoomID = `BuildingID + FloorNo + RoomNo`
//RoomName = `RoomName + RoomID`
const RoomSchema = new mongoose.Schema({
    RoomID : {type : Number},
    RoomName : {type : String, trim : true},
    Floor : {type: Number},
    Capacity : {type: Number, default : 40},
    RoomType : {
        type : String,
        default : "Classroom",
        enum : ["Classroom", "Lab", "Auditorium", "Mess", "Office", "Canteen"]
    }
});

const CampusBuildingSchema = new mongoose.Schema({
    BuildingID : {  type: Number },
    BuildingName : {type : String, trim : true},
    BuildingType : {
        type : String,
        enum : ['Academic','Administration','Student Residence','Faculty Residence','Staff Residence','Grounds','Restaurant','Market','Healthcare','Facility','Non_Academic','Mess','Gymkhana']
    },
    NoOfFloors: {type: Number},
    NumberofRoomsinEachFloor : {type: Number},
    NoOfWorkers: {type: Number},
    Status : {type : Boolean, default: true},
    ActiveHours : {
        start : {type : String},
        end : {type : String} 
    },
    BuildingImage_path : {type : String},
    BuildingCordinaties : {type : String},
    Rooms : [RoomSchema],
    campusname : CampusNames
});

CampusBuildingSchema.pre('insertMany', async function (next, docs) {
    //uniqueness validations
    next();
});

CampusBuildingSchema.methods.assignBuildingIDandRoomID = async function () {
    const Counter = require('./Counter');

    const campusCounter = await Counter.findOne({campusname: this.campusname});
    this.BuildingID = await campusCounter.increaseCount("CampusBuilding"); 
  
    (RoomCountPerFloor = []).length = this.NoOfFloors;
    RoomCountPerFloor.fill(1);
    for(let room of this.Rooms){
        room.RoomID = `${this.BuildingID}${room.Floor}${RoomCountPerFloor[room.Floor-1]}`;
        room.RoomName = `RoomName${room.RoomID}`;
        RoomCountPerFloor[room.Floor-1]++;
    }
    await this.save();
}

const CampusBuilding = mongoose.model("CampusBuilding", CampusBuildingSchema);

module.exports = CampusBuilding;