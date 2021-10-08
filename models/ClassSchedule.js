const mongoose = require('mongoose');
const ErrorResponse = require('../utils/errorResponse');

const ClassScheduleSchema = new mongoose.Schema({
    CourseID : { type: String, required: true},
    CourseName : {type : String, trim : true},
    BuildingName : {type : String},
    RoomName : {type : String, trim : true},
    Strength : { type: Number},
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
    campusname : { type: String, required: true, select: false }
});

ClassScheduleSchema.pre('insertMany', async function (next, docs) {
    const CampusBuilding = require("./CampusBuilding");
    const Faculty = require("./Faculty");
    try {
        tobeCourseID = [];
        for(let doc of docs){
            let isUniqueIDasperCampus = await doc.isUniqueIDasperCampus();
            if(!isUniqueIDasperCampus) {
                throw "One or more CourseIDs are already used in the database for your campus!";
            }
            tobeCourseID.push(doc.CourseID.toLowerCase());

            if(doc.BuildingName != undefined){
                let building = await CampusBuilding.findOne({BuildingName : doc.BuildingName, campusname : doc.campusname});
                if(!building){
                    throw `Building - ${doc.BuildingName} doesn't exist in your campus Building Database! First add buildings!`;
                }   
            }
            
            //adding courses to Faculty as per the CourseInstructor array
            for(let i=0; i < doc.CourseInstructor.length; i++){
                let fac = await Faculty.findOne({Name : doc.CourseInstructor[i], campusname : doc.campusname});
                if(!fac) {
                    throw `Faculty - ${doc.CourseInstructor[i]} doesn't exist in your campus Faculty database! Add him first!`;
                } 
                fac.Courses.push(doc.CourseID);
                await fac.save();
            }
        }
        if((new Set(tobeCourseID)).size !== tobeCourseID.length) {
            throw "Your upload contains duplicate CourseIDs for two or more courses!";
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