const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');

const CounterSchema = new mongoose.Schema({
    campusname : CampusNames,
    CampusBuilding : { type: Number},
    User : {type : Number},
    BatchStudent : {type : Number},
    Faculty : { type: Number},
    Staff : { type: Number}
});

const Counter = mongoose.model("Counter", CounterSchema);

module.exports = Counter;