const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');

const StaffSchema = new mongoose.Schema({
    StaffCategory : { type: Number},
    WorkplaceBuildingName : {type : String},
    ResidenceBuildingName : {type : String},
    AdultFamilyMembers : {type : Number},
    NoofChildren : { type: Number},
    campusname : CampusNames
});

const Staff = mongoose.model("Staff", StaffSchema);

module.exports = Staff;