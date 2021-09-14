const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');

const FacultySchema = new mongoose.Schema({       
    Name: {type:String, trim : true, required:true},
    Courses : [{type: String}],
    Department : {type : String, enum : ['Mech','Cse','IT']},
    ResidenceBuildingName : {type : String},
    AdultFamilyMembers : {type : Number},
    NoofChildren : { type: Number},
    campusname : CampusNames
});

const Faculty = mongoose.model("Faculty", FacultySchema);

module.exports = Faculty;