const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');
const ErrorResponse = require('../utils/errorResponse');

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
    BuildingName : {type : String, trim : true, required : true},
    BuildingType : {
        type : String,
        default : 'Academic',
        enum : ['Academic','Administration','Student Residence','Faculty Residence','Staff Residence','Grounds','Restaurant','Market','Healthcare','Facility','Non_Academic','Mess','Gymkhana']
    },
    NoOfFloors: {type: Number, required : true},
    NumberofRoomsinEachFloor : {type: Number, required : true},
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
    try{
        tobeNames = [];
        for(let doc of docs){            
            let isUniqueNameasperCampus = await doc.isUniqueNameasperCampus();
            if(!isUniqueNameasperCampus) {
                throw "One or more Building Names are already used in the database for your campus!"
            }
            tobeNames.push(doc.BuildingName.toLowerCase());
        }
        if((new Set(tobeNames)).size !== tobeNames.length) {
            throw "Your upload contains duplicate Building Names for two or more Buildings!"
        }
        next();
    } 
    catch (error) {
        return next(new ErrorResponse(error,400));
    }
});

CampusBuildingSchema.methods.isUniqueNameasperCampus = async function () {
    try {
        let building = await CampusBuilding.findOne({ campusname : this.campusname, BuildingName: this.BuildingName})
        if(building) {return false;}
        else {return true;}
    } catch(err){
        return err;
    }
}

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