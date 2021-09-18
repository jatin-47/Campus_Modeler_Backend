const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');

const ClassScheduleSchema = new mongoose.Schema({
    CourseID : { type: String, required: true},
    CourseName : {type : String, trim : true},
    BuildingName : {type : String},
    RoomName : {type : String, trim : true},
    Strength : { type: Number},
    Departments : [{type : String}],
    Status : {type : Boolean, default: true},
    ClassDays : [{
        Day : {type : String, enum : ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']},
        Timing : {
            start : {type : String},
            end : {type : String} 
        }
    }],
    CourseInstructor : [{type: String}],
    StudentComposition :[{
        BatchCode : {type : String},
        Count : {type : Number}
    }],
    campusname : CampusNames
});

ClassScheduleSchema.pre('insertMany', async function (next, docs) {
    const CampusBuilding = require("./CampusBuilding");
    try {
        const campusbuildings = await CampusBuilding.find({campusname : this.campusname});

        tobeCourseID = [];
        for(let doc of docs){
            let isUniqueIDasperCampus = await doc.isUniqueIDasperCampus();
            if(!isUniqueIDasperCampus) {
                throw "One or more CourseIDs are already used in the database for your campus!"
            }
            tobeCourseID.push(doc.CourseID.toLowerCase());

            // let building = await campusbuildings.findOne({BuildingName : doc.BuildingName});
            // if(building)
            //     doc.BuildingName = building._id;
        }
        if((new Set(tobeCourseID)).size !== tobeCourseID.length) {
            throw "Your upload contains duplicate CourseIDs for two or more courses!"
        }
        next();
    }
    catch (error) {
        return next(new ErrorResponse(error,400));
    }
});

ClassScheduleSchema.methods.isUniqueIDasperCampus = async function () {
    try {
        let course = await ClassSchedule.findOne({ campusname : this.campusname, CourseID: this.CourseID})
        if(course) {return false;}
        else {return true;}
    } catch(err){
        return err;
    }
}

const ClassSchedule = mongoose.model("ClassSchedule", ClassScheduleSchema);

module.exports = ClassSchedule;