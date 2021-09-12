const mongoose = require('mongoose');

const FacultySchema = new mongoose.Schema({       
    Courses : [{type: String}],
    Department : {type : String, enum : ['Mech','Cse','IT']},
    ResidenceBuildingName : {type : String},
    AdultFamilyMembers : {type : Number},
    NoofChildren : { type: Number}
});

const Faculty = mongoose.model("Faculty", FacultySchema);

module.exports = Faculty;