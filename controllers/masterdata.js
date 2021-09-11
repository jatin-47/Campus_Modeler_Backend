const User = require('../models/User');
const CampusBuilding = require('../models/CampusBuilding');
const ClassSchedule = require('../models/ClassSchedule');

const ErrorResponse = require('../utils/errorResponse');

exports.campusBuildings = async (request, response, next) => {

    let CampusBuildings = await CampusBuilding.find({}, 'BuildingID BuildingName BuildingType NoOfFloors NoOfWorkers Status');

    response.send(CampusBuildings);
};

exports.viewDataCampusBuildings = async (request, response, next) => {

    const { BuildingID } = request.query;
    let viewdata = await CampusBuilding.findOne({ BuildingID: BuildingID });
    response.send(viewdata);
};

exports.uploadCampusBuildings = async (request, response, next) => {

    const { file } = request.body;
    if( file == '.xlsl')
    {
        //to be done
        //resolving data from the xlsl sheet and saving that documnet to 'CampusBuilding' collection

        //test
        await CampusBuilding.create({ 
            BuildingID : 1234,
            BuildingName : 'Central Instrumentation Building',
            BuildingType : 'Acadamic',
            NoOfFloors : 3,
            NoOfWorkers : 75,
            Status : true , 
            ActiveHours : '',
            BuildingCordinaties : '',
            Rooms : [{
                RoomID : 1,
                RoomName : 'Basiclab',
                Floor : 1,
                capacity : 40,
                roomtype : 'lab'
            }]
        });

        response.send({
            success: true,
            message: 'uploaded successfully'
        });
    }
    else
    {
        response.send({
            success: false,
            message: 'wrong file format'
        });
    }    
};


exports.addBuildingCampusBuildings = async (request, response, next) => {

    
    //to be done
    //resolving data from the request body and saving that documnet to 'CampusBuilding' collection


    response.send({
        success: true,
        message: 'saved successfully'
    });
};

exports.deleteBuildingCampusBuildings = async (request, response, next) => {

    const { BuildingID } = request.query;
    await CampusBuilding.deleteOne({ BuildingID : BuildingID})

    response.send({
        success: true,
        message: 'deleted successfully'
    });
};

exports.classSchedule = async (request, response, next) => {

    let ClassSchedules = await ClassSchedule.find({}, 'CourseID CourseName RoomID Strength Departments Status');

    response.send(ClassSchedules);
};

exports.viewDetailsClassSchedule = async (request, response, next) => {

    const { CourseID } = request.query;
    let viewdata = await ClassSchedule.findOne({ CourseID: CourseID });
    response.send(viewdata);
};

exports.deleteClassClassSchedule = async (request, response, next) => {
    const { CourseID } = request.query;
    try {
        await ClassSchedule.deleteOne({ CourseID : CourseID})
        response.send({
            success: true,
            message: 'deleted successfully'
        });
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

exports.addClassClassSchedule = async (request, response, next) => {
    const data = request.body;

    await ClassSchedule.create({
        CourseID : data.CourseID,
        CourseName : data.CourseName,
        RoomID : await ClassSchedule.findOne({ RoomID: data.RoomID }, '_id'),
        Strength : data.Strength,
        Departments : data.Departments,
        Status : data.Status,
        ClassDays : [{
            Day : 'Monday',
            Timing : {
                start : "9am",
                end : "10am"
            }
        }],
        CourseInstructor : "staff",
        StudentComposition :[]
    });

    response.send({
        success: true,
        message: 'saved successfully'
    });
};

exports.getBuildingAddClassClassSchedule = async (request, response, next) => {
    const buildingnames = await CampusBuilding.find({}, 'BuildingName');

    response.send(buildingnames);
};

exports.getRoomIdAddClassClassSchedule = async (request, response, next) => {
    const roomids = await CampusBuilding.find({}, 'Rooms');

    response.send(roomids);
};

exports.getStudentStrengthAddClassClassSchedule = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.getCourseInstructorAddClassClassSchedule = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.addStudentCompositionAddClassClassSchedule = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.editStudentCompositionAddClassClassSchedule = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.deleteStudentCompositionAddClassClassSchedule = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.users = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.viewDetailsUsers = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.addUserUsers = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.surveyUploader = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.deleteSurveyUploader = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.updateSurveyUploader = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.downloadSurveyUploader = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.addCampusMapUploader = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.updateCampusMapUploader = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.addStudentDataUploader = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.deleteStudentDataUploader = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.updateStudentDataUploader = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.batchwiseStudentDetails = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.addBatchwiseStudentDetails = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.deleteBatchwiseStudentDetails = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.facultyDetails = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.addFacultyDetails = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.residenceBuildNameAddFacultyDetails = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.deleteFacultyDetails = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.staffDetails = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.addStaffDetails = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.deleteStaffDetails = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};
