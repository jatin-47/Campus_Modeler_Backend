const mongoose = require('mongoose');

const BatchStudentSchema = new mongoose.Schema({
    BatchCode : { 
        type: String, 
        unique:true,
        required: [true, "Input parameters cannot be empty!"] 
    },
    Department : {
        type : String,
        enum : ['Mech','Cse','IT']
    },
    ProgramCode : { type: String, enum : ["BE", "ME", "PHD"]},
    YearOfStudy : {type : Number},
    Strength : { type: Number},
    Status : {
        type : Boolean,
        default: true
    }
});

const BatchStudent = mongoose.model("BatchStudent", BatchStudentSchema);

module.exports = BatchStudent;