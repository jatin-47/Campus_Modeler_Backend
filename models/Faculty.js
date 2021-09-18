const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');

const FacultySchema = new mongoose.Schema({
    FacultyID : {type : Number},        
    Name: {type: String, trim : true, required : true},
    Courses : [{type: String}],
    Department : {type : String, required: true},
    ResidenceBuildingName : {type : String},
    AdultFamilyMembers : {type : Number, required: true},
    NoofChildren : { type: Number, required: true},
    campusname : CampusNames
});

FacultySchema.pre('insertMany', async function (next, docs) {
    //uniqueness validations
    next();
});

FacultySchema.methods.assignFacultyID = async function () {
    const Counter = require('./Counter');

    const campusCounter = await Counter.findOne({campusname: this.campusname});
    this.FacultyID = await campusCounter.increaseCount("Faculty"); 
    await this.save();
}

const Faculty = mongoose.model("Faculty", FacultySchema);

module.exports = Faculty;