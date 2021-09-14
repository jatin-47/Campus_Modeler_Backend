const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');

const RoomSchema = new mongoose.Schema({
    RoomID : {type : Number},
    RoomName : {type : String},
    Floor : {type: Number},
    Capacity : {type: Number},
    RoomType : {type : String}
});

const CampusBuildingSchema = new mongoose.Schema({
    BuildingID : { 
        type: Number, 
        unique: true,
        required: [true, "Input parameters cannot be empty!"] 
    },
    BuildingName : {
        type : String,
        trim : true
    },
    BuildingType : {
        type : String,
        enum : ['Academic','Administration','Student Residence','Faculty Residence','Staff Residence','Grounds','Restaurant','Market','Healthcare','Facility','Non_Academic','Mess','Gymkhana']
    },
    NoOfFloors: {type: Number},
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

const CampusBuilding = mongoose.model("CampusBuilding", CampusBuildingSchema);

module.exports = CampusBuilding;