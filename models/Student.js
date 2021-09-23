const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');

const StudentSchema = new mongoose.Schema({
    StudentID : {type : Number, required : true},        
    Age: {type: Number, required : true},
    HostelBuildingName : {type : String},
    MessBuildingName : {type:String},
    Year : {type : Number},
    Department : {type : String},
    Program : {type : String},
    Batch : {type : String},
    inCampus : {
        type : Number,
        enum : [0,1]
    },
    Courses : [{type : String}],
    campusname : CampusNames
});

StudentSchema.pre('insertMany', async function (next, docs) {
    //uniqueness validations
    next();
});

/* StudentSchema.methods.assignStudentID = async function () {
    const Counter = require('./Counter');

    const campusCounter = await Counter.findOne({campusname: this.campusname});
    this.StudentID = await campusCounter.increaseCount("Student"); 
    await this.save();
} */

const Student = mongoose.model("Student", StudentSchema);

module.exports = Student;