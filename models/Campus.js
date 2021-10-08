const mongoose = require('mongoose');
const ErrorResponse = require('../utils/errorResponse');

const CampusSchema = new mongoose.Schema({
    campusname : {type: String, trim : true, required : true},
    latitude : { type: Number, required: true},
    longitude : { type: Number, required: true}
});

const Campus = mongoose.model("Campus", CampusSchema);

module.exports = Campus;