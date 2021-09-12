const mongoose = require('mongoose');

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
        enum : ['Academic','Administartion']
    },
    NoOfFloors: {type: Number},
    NoOfWorkers: {type: Number},
    Status : {type : Boolean, default: true},
    ActiveHours : {
        start : {type : String},
        end : {type : String} 
    },
    BuildingCordinaties : {type : String},
    Rooms : [RoomSchema]
});

const CampusBuilding = mongoose.model("CampusBuilding", CampusBuildingSchema);

module.exports = CampusBuilding;