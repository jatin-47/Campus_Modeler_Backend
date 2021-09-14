const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');

const ClassScheduleSchema = new mongoose.Schema({
    CourseID : { 
        type: String, 
        unique:true,
        required: [true, "Input parameters cannot be empty!"] 
    },
    CourseName : {
        type : String,
        trim : true
    },
    BuildingName : {
        type : mongoose.Schema.Types.ObjectId,
        ref : 'CampusBuilding'
    },
    RoomID : {
        type : mongoose.Schema.Types.ObjectId
    },
    Strength : {
        type: Number
    },
    Departments : [{
        type : String,
        enum : ['Mech','Cse','IT']
    }],
    Status : {
        type : Boolean,
        default: true
    },
    ClassDays : [{
        Day : {type : String, enum : ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']},
        Timing : {
            start : {type : String},
            end : {type : String} 
        }
    }],
    CourseInstructor : {type : String},
    StudentComposition :[{
       BatchCode : {type : String},
       Count : {type : Number}
    }],
    campusname : CampusNames
});

const ClassSchedule = mongoose.model("ClassSchedule", ClassScheduleSchema);

module.exports = ClassSchedule;