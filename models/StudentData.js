const mongoose = require('mongoose');

const StudentDataSchema = new mongoose.Schema({
    filename :  {
        type: String, 
        unique : true,
        required :  [true, "Input parameters cannot be empty!"] 
    },
    path : {
        type: String, 
        required :  [true, "Input parameters cannot be empty!"] 
    }
}, { timestamps: true });

const StudentData = mongoose.model("StudentData", StudentDataSchema);

module.exports = StudentData;