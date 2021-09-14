const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');

const CampusMapSchema = new mongoose.Schema({
    filename :  {
        type: String, 
        unique : true,
        required :  [true, "Input parameters cannot be empty!"] 
    },
    path : {
        type: String, 
        required :  [true, "Input parameters cannot be empty!"] 
    },
    LatitudeRange : {
        start : {type : Number},
        end : {type : Number}
    },
    LongitudeRange : {
        start : {type : Number},
        end : {type : Number}
    },
    campusname : CampusNames

}, { timestamps: true });

const CampusMap = mongoose.model("CampusMap", CampusMapSchema);

module.exports = CampusMap;