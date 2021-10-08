const mongoose = require('mongoose');
const ErrorResponse = require('../utils/errorResponse');

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
    SurveyType : {
        type : String,
        enum : ["Student Survey", "Staff Survey"]
    },
    campusname : { type: String, required: true, select: false }

}, { timestamps: true });

const Survey = mongoose.model("Survey", SurveySchema);

module.exports = Survey;