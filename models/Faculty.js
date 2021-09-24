const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');
const ErrorResponse = require('../utils/errorResponse');

const FacultySchema = new mongoose.Schema({
    FacultyID : {type : Number},        
    Name: {type: String, trim : true, required : true},
    Courses : [{type: String}],
    Department : {type : String, required: true},
    ResidenceBuildingName : {type : String},
    AdultFamilyMembers : {type : Number, required: true},
    NoofChildren : { type: Number, required: true},
    campusname : CampusNames
});

FacultySchema.pre('insertMany', async function (next, docs) {
    const CampusBuilding = require("./CampusBuilding");
    try{
        for(let doc of docs){
            let building = await CampusBuilding.findOne({BuildingName : doc.ResidenceBuildingName, campusname : doc.campusname});
            if(!building){
                throw `Building - ${doc.ResidenceBuildingName} doesn't exist in your campus Building Database! First add buildings!`
            }
        }
        next();
    }
    catch (error) {
        return next(new ErrorResponse(error,400));
    }
});

FacultySchema.methods.assignFacultyID = async function () {
    const Counter = require('./Counter');

    const campusCounter = await Counter.findOne({campusname: this.campusname});
    this.FacultyID = await campusCounter.increaseCount("Faculty"); 
    await this.save();
}

const Faculty = mongoose.model("Faculty", FacultySchema);

module.exports = Faculty;