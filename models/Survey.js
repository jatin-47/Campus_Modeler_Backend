const mongoose = require('mongoose');

const SurveySchema = new mongoose.Schema({
    filename :  {
        type: String, 
        unique : true,
        required :  [true, "Input parameters cannot be empty!"] 
    },
    path : {
        type: String, 
        required :  [true, "Input parameters cannot be empty!"] 
    },
    filetype : {
        type : String,
        enum : [".xlsx"]
    },
    SurveyType : {
        type : String,
        enum : ["Student Survey", "Staff Survey"]
    }
}, { timestamps: true });

const Survey = mongoose.model("Survey", SurveySchema);

module.exports = Survey;