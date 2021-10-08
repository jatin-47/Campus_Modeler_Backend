const mongoose = require('mongoose');
const ErrorResponse = require('../utils/errorResponse');

const StaffSchema = new mongoose.Schema({
    StaffID : { type : Number },
    StaffCategory : { type: Number},
    WorkplaceBuildingName : {type : String},
    ResidenceBuildingName : {type : String},
    AdultFamilyMembers : {type : Number, required : true},
    NoofChildren : { type: Number, required: true},
    campusname : { type: String, required: true, select: false }
});

StaffSchema.methods.assignStaffID = async function () {
    const Counter = require('./Counter');

    const campusCounter = await Counter.findOne({campusname: this.campusname});
    this.StaffID = await campusCounter.increaseCount("Staff"); 
    await this.save();
}

const Staff = mongoose.model("Staff", StaffSchema);

module.exports = Staff;