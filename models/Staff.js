const mongoose = require('mongoose');

const StaffSchema = new mongoose.Schema({
    StaffCategory : { type: Number},
    WorkplaceBuildingName : {type : String},
    ResidenceBuildingName : {type : String},
    AdultFamilyMembers : {type : Number},
    NoofChildren : { type: Number}
});

const Staff = mongoose.model("Staff", StaffSchema);

module.exports = Staff;