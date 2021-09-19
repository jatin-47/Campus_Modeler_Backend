const User = require('../models/User');
const CampusBuilding = require('../models/CampusBuilding');
const ClassSchedule = require('../models/ClassSchedule');
const BatchStudent = require('../models/BatchStudent');
const Faculty = require('../models/Faculty');
const Student = require('../models/Student');
const Staff = require('../models/Staff');
const Survey = require('../models/Survey');
const StudentData = require('../models/StudentData');

const ErrorResponse = require('../utils/errorResponse');
var fs = require('fs');
const PATH = require('path');
const readXlsxFile = require('read-excel-file/node');
const excel = require("exceljs");

/****************************************************************/

exports.campusBuildings = async (request, response, next) => {
    try {
        let CampusBuildings = await CampusBuilding.find({campusname : request.user.campusname}, 'BuildingID BuildingName BuildingType NoOfFloors NoOfWorkers Status');
        response.send(CampusBuildings);
    }
    catch(err){ return next(new ErrorResponse(err, 400)); }
};

exports.viewDataCampusBuildings = async (request, response, next) => {
    try {
        const { BuildingID } = request.query;
        let viewdata = await CampusBuilding.findOne({_id: BuildingID, campusname : request.user.campusname});
        response.send(viewdata);
    }
    catch(err){  return next(new ErrorResponse(err,400));  }
};

exports.templateCampusBuildings = async (request, response, next) => {
    const workbook = new excel.Workbook();
    const filename = "Building_template";
    const sheet = workbook.addWorksheet(filename);

    sheet.columns = [
        { header: "Building Name"},
        { header: "Building Type"},
        { header: "Building Status"},
        { header: "Number of Floors"},
        { header: "Number of Rooms in Each Floor"},
        { header: "Number of Workers"},
        { header: "Active Hours (start)"},
        { header: "Active Hours (end)"},
        { header: "Building Polygon"}
      ];
  
    response.setHeader(
    "Content-Type",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    );
    response.setHeader(
    "Content-Disposition",
    "attachment; filename=" + filename + ".xlsx"
    );

    return workbook.xlsx.write(response).then(function () {
        response.status(200).end();
    });
};

exports.uploadCampusBuildings = async (request, response, next) => {
    try {
        if (request.file == undefined) {
            return next(new ErrorResponse("Please upload an excel file!",400));
        }
        let path = request.file.path;
    
        let rows = await readXlsxFile(path);

        const required_headers = ["Building Name","Building Type","Building Status","Number of Floors","Number of Rooms in Each Floor", "Number of Workers","Active Hours (start)","Active Hours (end)","Building Polygon"];
        let header = rows.shift();

        for(let i=0; i<required_headers.length; i++){
            if(header[i] != required_headers[i])
                throw "Wrong headers! please match with template file!";
        }
    
        let buildings = [];
    
        rows.forEach((row) => {
            let Rooms = [];
            for(let floor = 1; floor <= row[3]; floor++){
                for(let room = 0; room < row[4]; room++){
                    let Room = {Floor : floor};
                    Rooms.push(Room);
                }
            }
            let building = new CampusBuilding({
                BuildingName : row[0].trim(),
                BuildingType : row[1],
                Status : row[2].trim() == "Enabled" ? true : false, 
                NoOfFloors : row[3],
                NumberofRoomsinEachFloor : row[4],
                NoOfWorkers : row[5],
                ActiveHours : {
                    start : row[6],
                    end : row[7]
                },
                BuildingCordinaties : row[8],
                Rooms : Rooms,
                campusname : request.user.campusname
            });    
            buildings.push(building);
        });

        const docs = await CampusBuilding.insertMany(buildings);
        if(docs) {
            for(let doc of docs){
                await doc.assignBuildingIDandRoomID();
            }
        }

        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        try{
            fs.unlinkSync(request.file.path);
        }catch(err) {
            return next(new ErrorResponse("Could not delete the temp file!(internal err) " + err, 500));
        }
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

exports.uploadspecialrooms = async (request, response, next) => {
    try {
        if (request.file == undefined) {
            return next(new ErrorResponse("Please upload an excel file!",400));
        }
        let path = request.file.path;

        const jsonString = fs.readFileSync(path,{encoding:'utf8'});
        const data = JSON.parse(jsonString);

        /*
        {
            "BuildingName": [
                {
                    "RoomName" : ,
                    "Floor" : ,
                    "Capacity" : ,
                    "RoomType" : 
                },
                {
                    "RoomName" : ,
                    "Floor" : ,
                    "Capacity" : ,
                    "RoomType" : 
                }
            ],
        }
        */
        for (let BuildingName in data) {
            let building = await CampusBuilding.findOne({BuildingName: BuildingName, campusname : request.user.campusname});
            let rooms = data[BuildingName];

            for(let i =1; i <= building.NoOfFloors; i++){
                let givenRooms = rooms.filter((room) => room.Floor == i);
                let tobeModifiedRooms = building.Rooms.filter((room) => room.Floor == i);
                if(givenRooms.length > tobeModifiedRooms.length) 
                    throw "Rooms per floor exceeds limit!";
                for(let j=0; j<givenRooms.length; j++){
                    tobeModifiedRooms[j].RoomName = givenRooms[j].RoomName.trim();
                    tobeModifiedRooms[j].Capacity = givenRooms[j].Capacity;
                    tobeModifiedRooms[j].RoomType = givenRooms[j].RoomType.trim();
                }
            }
            building.markModified('Rooms'); 
            await building.save();
        }

        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        try{
            fs.unlinkSync(request.file.path);
        }catch(err) {
            return next(new ErrorResponse("Could not delete the temp file!(internal err) " + err, 500));
        }
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

exports.addBuildingCampusBuildings = async (request, response, next) => {
    try {
        const data = request.body;
        const { BuildingID } = request.query;
        if (request.file !== undefined) {
            var path = request.file.path;
        }

        if(BuildingID){ //update roomdetails
            if(!data.RoomDetails) {
                throw "Please provide RoomDetails also!"
            }
            let building = await CampusBuilding.findOne({_id: BuildingID, campusname : request.user.campusname});
            
            data.RoomDetails.forEach((room)=>{
                let tobeModifiedRoom = building.Rooms.id(room._id);
                tobeModifiedRoom.RoomName = room.RoomName.trim();
                tobeModifiedRoom.Capacity = room.Capacity;
                tobeModifiedRoom.RoomType = room.RoomType.trim();
            });
            building.markModified('Rooms'); 
            await building.save();

            response.send({
                success: true,
                message: 'Rooms updated successfully'
            });
        }
        else { // create a new building and return roomdetails

            let Rooms = [];
            for(let floor = 1; floor <= data.NoOfFloors; floor++){
                for(let room = 0; room < data.NumberofRoomsinEachFloor; room++){
                    let Room = {Floor : floor};
                    Rooms.push(Room);
                }
            }
            const doc = await CampusBuilding.create({ 
                BuildingName : data.BuildingName.trim(),
                BuildingType : data.BuildingType.trim(),
                NoOfFloors : data.NoOfFloors,
                NumberofRoomsinEachFloor : data.NumberofRoomsinEachFloor,
                NoOfWorkers : data.NoOfWorkers,
                ActiveHours : {
                    start : data.ActiveHours.split('"')[1],
                    end : data.ActiveHours.split('"')[3]
                },
                BuildingImage_path : path,
                BuildingCordinaties :data.BuildingCordinaties,
                Rooms : Rooms,
                campusname : request.user.campusname,
            });
            
            await doc.assignBuildingIDandRoomID();
    
            response.send({
                success: true,
                message: 'Saved successfully',
                BuildingID : doc._id,
                RoomDetails : doc.Rooms
            });
        }
    }
    catch(err){
        return next(new ErrorResponse(err,400));
    }
};

exports.deleteBuildingCampusBuildings = async (request, response, next) => {
    try {
        const { BuildingID } = request.query;
        await CampusBuilding.deleteOne({ campusname : request.user.campusname, _id : BuildingID})
    
        response.send({
            success: true,
            message: 'deleted successfully'
        });

    } catch(err){  return next(new ErrorResponse(err,400));  }
};

/****************************************************************/

exports.classSchedule = async (request, response, next) => {

    try{
        let ClassSchedules = await ClassSchedule.find({campusname : request.user.campusname}, 'CourseID CourseName BuildingName RoomName Strength Departments Status');
        response.send(ClassSchedules);
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

exports.viewDetailsClassSchedule = async (request, response, next) => {
    try{
        const { CourseID } = request.query;
        let viewdata = await ClassSchedule.findOne({ _id: CourseID, campusname : request.user.campusname });
        response.send(viewdata);
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

exports.deleteClassClassSchedule = async (request, response, next) => {
    try {
        const { CourseID } = request.query;
        await ClassSchedule.deleteOne({  _id : CourseID, campusname : request.user.campusname})
        response.send({
            success: true,
            message: 'deleted successfully'
        });
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

exports.templateclassschedule = async (request, response, next) => {
    const workbook = new excel.Workbook();
    const filename = "ClassSchedule_template";
    const sheet = workbook.addWorksheet(filename);

    sheet.columns = [
        { header: "Course ID"},
        { header: "Course Name"},
        { header: "Building Name"},
        { header: "Room Name"},
        { header: "Scheduled Days"},
        { header: "Scheduled Time"},
        { header: "Total Strength"},
        { header: "Course Instructor(s)"}
      ];
  
    response.setHeader(
    "Content-Type",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    );
    response.setHeader(
    "Content-Disposition",
    "attachment; filename=" + filename + ".xlsx"
    );

    return workbook.xlsx.write(response).then(function () {
        response.status(200).end();
    });
};

exports.uploadclassschedule = async (request, response, next) => {
    try {
        if (request.file == undefined) {
            return next(new ErrorResponse("Please upload an excel file!",400));
        }
        let path = request.file.path;
    
        let rows = await readXlsxFile(path);

        const required_headers = ["Course ID","Course Name","Building Name","Room Name","Scheduled Days", "Scheduled Time","Total Strength","Course Instructor(s)"];
        let header = rows.shift();

        for(let i=0; i<required_headers.length; i++){
            if(header[i] != required_headers[i])
                throw "Wrong headers! please match with template file!";
        }

        let courses = [];

        rows.forEach((row) => {
            let days = [];
            let times = [];
            if (row[4] == null) {
                row[4] = undefined;
                row[5] = undefined;
            } else{
                days = row[4].split(",").map((day)=>day.trim().toLowerCase());
                times = row[5].split(",").map((timing) => {
                    let time = {
                        start : timing.split("-")[0].trim(),
                        end : timing.split("-")[1].trim()
                    };
                    return time;
                });
            }
            let classdays = [];
            for(let i=0; i < days.length; i++){
                classdays.push({
                    Day : days[i],
                    Timing : times[i]
                });
            }
            if(row[2] == null) row[2] = undefined;
            if(row[3] == null) row[3] = undefined;
            let course = new ClassSchedule({
                CourseID : row[0].trim(),
                CourseName : row[1],
                CourseInstructor : String(row[7]).split(","),
                BuildingName : row[2],
                RoomName : row[3],
                ClassDays : classdays,
                Strength : row[6],
                StudentComposition :[],
                campusname : request.user.campusname
            }); 
            courses.push(course);
        });

        await ClassSchedule.insertMany(courses);     
        await addFacultyCourseDetails(courses);
        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        try{
            fs.unlinkSync(request.file.path);
        }catch(err) {
            return next(new ErrorResponse("Could not delete the temp file!(internal err) " + err, 500));
        }
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

async function addFacultyCourseDetails(courses){
    for(let i=0;i<courses.length;i++){
        for(let j=0;j<courses[i].CourseInstructor.length;j++){
            let fac = await Faculty.findOne({Name: courses[i].CourseInstructor}).exec();
            if(fac==null || fac==undefined)
                continue;
            fac.Courses.push(courses[i].CourseName);
            fac.save();
        }   
    }
}

exports.addClassClassSchedule = async (request, response, next) => {
    try{
        const data = request.body;
        const building = await CampusBuilding.findOne({campusname : request.user.campusname, BuildingName:data.BuildingName});
        if(!building) throw "No such building found in which this class is scheduled!";

        const room = building.Rooms.filter((room)=> room.RoomName==data.RoomName.trim()); 
        if(room.length == 0) throw "No such room found in which this class is scheduled!";
        
        let faculty = await Faculty.findOne({Name : data.CourseInstructor, campusname : request.user.campusname});
        if(!faculty) throw "No such faculty found!";

        let batch_id = data.StudentComposition.map(async (batch) => {
            let Batch = await BatchStudent.findOne({BatchCode: batch.BatchCode, campusname : request.user.campusname});
            if(!Batch) throw "No such batch found!";
            batch.BatchCode = Batch._id;
            return batch;
        });

        let classdays = data.ClassDays.map((curr) => { 
            curr.Timing = {
                start: curr.split("-")[0].trim(), 
                end: curr.split("-")[0].trim()
            };
            return curr
        });

        course = await ClassSchedule.create({
            CourseID : data.CourseID,
            CourseName : data.CourseName,
            BuildingName : data.BuildingName,
            RoomName :room[0].RoomName,
            Strength : data.Strength,
            Departments : data.Departments.split(","),
            Status : true,
            ClassDays : classdays,
            CourseInstructor : String(data.CourseInstructor),
            StudentComposition : data.StudentComposition,
            campusname : request.user.campusname
        });
        let fac = await Faculty.findOne({Name: courses[i].CourseInstructor}).exec();
        if(fac==null || fac==undefined){
            fac.Courses.push(courses[i].CourseName);
            fac.save();
        }
        response.send({
            success: true,
            message: 'saved successfully'
        });
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

exports.getBuildingAddClassClassSchedule = async (request, response, next) => {
    try{
        const buildingnames = await CampusBuilding.find({campusname : request.user.campusname}, 'BuildingName');
        response.send(buildingnames);
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

exports.getRoomIdAddClassClassSchedule = async (request, response, next) => {
    try{
        const { BuildingId } = request.query;
        const building = await CampusBuilding.findOne({campusname : request.user.campusname, _id : BuildingId}, 'Rooms');
        response.send(building); 
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

exports.getCourseInstructorAddClassClassSchedule = async (request, response, next) => {
    try {
        let faculties = await Faculty.find({campusname : request.user.campusname}, 'Name');
        response.send(faculties);
    }
    catch(err){  return next(new ErrorResponse(err,400));  }
};

//Not used 
exports.getStudentStrengthAddClassClassSchedule = async (request, response, next) => {

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
//Not used

/****************************************************************/

exports.users = async (request, response, next) => {

    try{
        let viewdata = await User.find({campusname : request.user.campusname}, 'UserID username role email contact status');
        response.send(viewdata);
    }catch(err){ return next(new ErrorResponse(err, 400)); }   
    
};

exports.viewDetailsUsers = async (request, response, next) => {
    try{
        const { UserID } = request.query;
        let userdata = await User.findOne({ _id : UserID, campusname : request.user.campusname}, '+photo_path');
        response.send(userdata);
    }
    catch(err){ return next(new ErrorResponse(err, 400)); }   
};

exports.templateusers = async (request, response, next) => {
    const workbook = new excel.Workbook();
    const filename = "User_template";
    const sheet = workbook.addWorksheet(filename);

    sheet.columns = [
        { header: "First Name"},
        { header: "Last Name"},
        { header: "DOB"},
        { header: "Gender"},
        { header: "Email ID"},
        { header: "Phone No"},
        { header: "User Role"},
        { header: "Status"},
        { header: "Temp Password"}
    ];
  
    response.setHeader(
    "Content-Type",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    );
    response.setHeader(
    "Content-Disposition",
    "attachment; filename=" + filename + ".xlsx"
    );

    return workbook.xlsx.write(response).then(function () {
        response.status(200).end();
    });
};
 
exports.uploadusers = async (request, response, next) => {
    try {
        if (request.file == undefined) {
            return next(new ErrorResponse("Please upload an excel file!",400));
        }
        //console.log(request.file);
        let path = request.file.path;
    
        let rows = await readXlsxFile(path);
        
        const required_headers = ["First Name", "Last Name","DOB","Gender","Email ID","Phone No","User Role","Status","Temp Password"];
        let header = rows.shift();

        for(let i=0; i<required_headers.length; i++){
            if(header[i] != required_headers[i])
                throw "Wrong headers! please match with template file!";
        }
    
        let users = [];
    
        rows.forEach((row) => {
            let user = new User({
                fname : row[0].trim(),
                lname : row[1].trim(),
                dob : row[2],
                gender : row[3].trim(),
                email : row[4].trim().toLowerCase(), 
                contact : row[5],
                role : row[6].trim(),
                status : row[7].trim() == "Enabled" ? true : false,
                password : row[8],
                campusname : request.user.campusname
            }); 
            users.push(user);
        });

        const docs = await User.insertMany(users);
        if(docs){            
            for(let doc of docs){
                await doc.assignUserID();
            }
        }
 
        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        try{
            fs.unlinkSync(request.file.path);
        }catch(err) {
            return next(new ErrorResponse("Could not delete the temp file!(internal err) " + err, 500));
        }
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

exports.addUserUsers = async (request, response, next) => {
    try{
        const data = request.body;
        if (request.file !== undefined) {
            var path = request.file.path;
        }
        const doc = await User.create({
            username: data.Username,
            email: data.Email.trim().toLowerCase(),
            password: data.Password,
            role: data.Role,
            campusname: request.user.campusname,
            fname : data.Fname,
            lname :data.Lname,
            gender :data.Gender,
            contact : data.Contact,
            dob : data.DOB,
            photo_path : path
        });  
        await doc.assignUserID();

        response.send({
            success: true,
            message: 'saved successfully'
        }); 
    }
    catch(err){ return next(new ErrorResponse(err, 400)); }
};

/****************************************************************/

exports.surveyUploader = async (request, response, next) => {
    if (request.file == undefined) {
        return next(new ErrorResponse("Please upload an excel file!",400));
    }
    try {
        await Survey.create({
            filename :  request.file.filename,
            path : __basedir + process.env.EXCEL_UPLOAD_PATH,
            filetype : request.file.filetype,
            SurveyType : request.body.SurveyType,
            campusname : request.user.campusname
        })
        response.status(200).send({
            message: "Uploaded the file successfully: " + request.file.originalname,
        });
    }
    catch (error) {
        console.log(error);
        response.status(500).send({
            message: "Could not upload the file: " + request.file.originalname,
        });
    }
};

exports.deleteSurveyUploader = async (request, response, next) => {
    const { SurveyID } = request.query;
    try {
        const survey = await Survey.findByID(SurveyID);
        const path = survey.path;
        const filename = survey.filename;

        fs.unlink(path.join(path.filename), function (err) {
            if (err) throw err;
            console.log('File deleted!');
        });

        response.send({
            success: true,
            message: 'deleted successfully'
        });

    } catch(err){  return next(new ErrorResponse(err,400));  }
};

exports.updateSurveyUploader = async (request, response, next) => {
    if (request.file == undefined) {
        return next(new ErrorResponse("Please upload an excel file!",400));
    }
    try {
        const survey = await Survey.findByID(SurveyID);
        const path = survey.path;
        const filename = survey.filename;

        fs.writeFile(path.join(path.filename), function (err) {
            if (err) throw err;
            console.log('Replaced!');
        });

        response.send({
            success: true,
            message: 'deleted successfully'
        });
    }
    catch (error) {
        console.log(error);
        response.status(500).send({
            message: "Could not upload the file: " + request.file.originalname,
        });
    }
};

exports.downloadSurveyUploader = async (request, response, next) => {
    ////
    
    response.setHeader(
        "Content-Type",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    );
    response.setHeader(
        "Content-Disposition",
        "attachment; filename=" + "survey.xlsx"
    );
    response.attachment("survey.xlsx");
    response.send();
};

/****************************************************************/

exports.addCampusMapUploader = async (request, response, next) => {
        
    response.status(200).send({
        message: "Uploaded the file successfully: " + request.file.originalname,
    });
};

exports.updateCampusMapUploader = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

/****************************************************************/

exports.addStudentDataUploader = async (request, response, next) => {
    try {
        if (request.file == undefined) {
            return next(new ErrorResponse("Please upload an excel file!",400));
        }
        let path = request.file.path;
    
        let rows = await readXlsxFile(path);

        const required_headers = ["Student ID","Age","Hostel Building Name","Mess Building Name","Year","Department", "Program","Batch","inCampus"];
        let header = rows.shift();
        for(let i=0; i<required_headers.length; i++){
            if(header[i] != required_headers[i])
                throw "Wrong headers! please match with template file!";
        }

        let students = [];
        rows.forEach((row) => {
            let student = new Student({
                StudentID : row[0],
                Age : row[1],
                HostelBuildingName : row[2].trim(),
                MessBuildingName : row[3].trim(),
                Year : row[4],
                Department : row[5],
                Program :row[6].trim(),
                Batch : row[7],
                inCampus : row[8],
                Courses : [],
                campusname : request.user.campusname
            }); 
            students.push(student);
        });

        await Student.insertMany(students);
 
        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        try{
            fs.unlinkSync(request.file.path);
        }catch(err) {
            return next(new ErrorResponse("Could not delete the temp file!(internal err) " + err, 500));
        }
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

exports.deleteStudentDataUploader = async (request, response, next) => {
    const { StudentdataID } = request.query;
    try {
        
        await StudentData.findByIdAndDelete(StudentdataID);

        // also delete file from server
         
        response.send({
            success: true,
            message: 'deleted successfully'
        });

    } catch(err){  return next(new ErrorResponse(err,400));  }
};

exports.updateStudentDataUploader = async (request, response, next) => {
    if (request.file == undefined) {
        return next(new ErrorResponse("Please upload an excel file!",400));
    }
    try {

    }
    catch (error) {
        console.log(error);
        response.status(500).send({
            message: "Could not upload the file: " + request.file.originalname,
        });
    }
};

/****************************************************************/

exports.batchwiseStudentDetails = async (request, response, next) => {
    try{
        let viewdata = await BatchStudent.find({campusname : request.user.campusname});
        response.send(viewdata);
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

exports.templatebatchwisestudentdetails = async (request, response, next) => {
    const workbook = new excel.Workbook();
    const filename = "BatchwiseStudent_template";
    const sheet = workbook.addWorksheet(filename);

    sheet.columns = [
        { header: "Batch Code"},
        { header: "Year of Study"},
        { header: "Department Code"},
        { header: "Program Code"},
        { header: "Strength"}
    ];
  
    response.setHeader(
    "Content-Type",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    );
    response.setHeader(
    "Content-Disposition",
    "attachment; filename=" + filename + ".xlsx"
    );

    return workbook.xlsx.write(response).then(function () {
        response.status(200).end();
    });
};

exports.uploadbatchwisestudentdetails = async (request, response, next) => {
    try {
        if (request.file == undefined) {
            return next(new ErrorResponse("Please upload an excel file!",400));
        }
        let path = request.file.path;
    
        let rows = await readXlsxFile(path);

        const required_headers = ["Batch Code", "Year of Study", "Department Code", "Program Code" , "Strength"];
        let header = rows.shift();

        for(let i=0; i<required_headers.length; i++){
            if(header[i] != required_headers[i])
                throw "Wrong headers! please match with template file!";
        }
    
        let batchStudents = [];

        rows.forEach((row) => {
            let batchStudent = new BatchStudent({
                BatchCode : row[0].trim(),
                Department : row[2],
                ProgramCode : String(row[3]),
                YearOfStudy : row[1],
                Strength : row[4],
                campusname : request.user.campusname
            });
            batchStudents.push(batchStudent);
        });

        const docs = await BatchStudent.insertMany(batchStudents);
        if(docs){            
            for(let doc of docs){
                await doc.assignBatchID();
            }
        }

        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        try{
            fs.unlinkSync(request.file.path);
        }catch(err) {
            return next(new ErrorResponse("Could not delete the temp file!(internal err) " + err, 500));
        }
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

exports.uploadbatchwiseDistribution = async (request, response, next) => {
    try {
        if (request.file == undefined) {
            return next(new ErrorResponse("Please upload an json file!",400));
        }
        let path = request.file.path;

        const jsonString = fs.readFileSync(path,{encoding:'utf8'});
        const data = JSON.parse(jsonString);

        /*
        {
            "B15BS": {
                "BS322": "1",
                "BS398": "1",
                "CS212": "1",
                "CS312": "1",
                "MA111": "1",
                "MA221": "1"
            },
            "B15CS": {
                "HS411": "1",
                "HSL4010": "2",
                "HSL4020": "1",
                "HSL6010": "1",
                "HSL7310": "1",
                "MA221": "1"
            },
        }
        */
        for (let BatchName in data){
            (async function() {
                for(let CourseName in data[BatchName]) {
                    let course = await ClassSchedule.findOne({CourseName: CourseName, campusname : request.user.campusname});
                    if(course){
                        course.StudentComposition.push({
                            BatchCode : BatchName,
                            Count : parseInt(data[BatchName][CourseName])
                        });
                        course.save();
                    }
                }
             })();
        }
        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        try{
            fs.unlinkSync(request.file.path);
        }catch(err) {
            return next(new ErrorResponse("Could not delete the temp file!(internal err) " + err, 500));
        }
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

exports.addBatchwiseStudentDetails = async (request, response, next) => {
    try{
        const data = request.body;
        const doc = await BatchStudent.create({
            BatchCode : data.BatchCode,
            Department : data.Department,
            ProgramCode : String(data.ProgramCode),
            YearOfStudy : data.YearOfStudy,
            Strength : data.Strength,
            campusname : request.user.campusname
        });  
        await doc.assignBatchID();

        response.send({
            success: true,
            message: 'saved successfully'
        }); 

    }catch(err){ return next(new ErrorResponse(err, 400)); }
};

exports.deleteBatchwiseStudentDetails = async (request, response, next) => {
    try {
        const { BatchID } = request.query;
        await BatchStudent.findByIdAndDelete(BatchID);
        response.send({
            success: true,
            message: 'deleted successfully'
        });
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

/****************************************************************/

exports.facultyDetails = async (request, response, next) => {
    try{
        let viewdata = await Faculty.find({campusname : request.user.campusname});
        response.send(viewdata);
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

exports.templatefacultydetails = async (request, response, next) => {
    const workbook = new excel.Workbook();
    const filename = "Faculty_template";
    const sheet = workbook.addWorksheet(filename);

    sheet.columns = [
        { header: "Name"},
        { header: "Residence_Building_Name"},
        { header: "Department_Code"},
        { header: "No_of_Adult_Family_Members"},
        { header: "No_of_Children"}
    ];
  
    response.setHeader(
    "Content-Type",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    );
    response.setHeader(
    "Content-Disposition",
    "attachment; filename=" + filename + ".xlsx"
    );

    return workbook.xlsx.write(response).then(function () {
        response.status(200).end();
    });
};

exports.uploadfacultydetails = async (request, response, next) => {
    try {
        if (request.file == undefined) {
            return next(new ErrorResponse("Please upload an excel file!",400));
        }
        let path = request.file.path;
    
        let rows = await readXlsxFile(path);

        const required_headers = ["Name" , "Residence_Building_Name", "Department_Code", "No_of_Adult_Family_Members", "No_of_Children"];
        let header = rows.shift();

        for(let i=0; i<required_headers.length; i++){
            if(header[i] != required_headers[i])
                throw "Wrong headers! please match with template file!";
        }

        let faculties= [];

        rows.forEach((row) => {
            let faculty= new Faculty( {
                Name : String(row[0]),
                Courses : [],
                ResidenceBuildingName: String(row[1]),
                Department : row[2],
                AdultFamilyMembers : row[3],
                NoofChildren : row[4],
                campusname : request.user.campusname
            }); 
            faculties.push(faculty);
        });

        const docs = await Faculty.insertMany(faculties);
        if(docs){            
            for(let doc of docs){
                await doc.assignFacultyID();
            }
        }

        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        try{
            fs.unlinkSync(request.file.path);
        }catch(err) {
            return next(new ErrorResponse("Could not delete the temp file!(internal err) " + err, 500));
        }
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

exports.addFacultyDetails = async (request, response, next) => {
    try{
        const data = request.body;

        let building = await CampusBuilding.findOne({BuildingName: data.BuildingName, campusname : request.user.campusname}) 
        if(!building) throw "No such building exists in your campus!"

        const doc = await Faculty.create({
            Name : data.Name,
            Courses : data.Courses.split(",").map((curr) => curr.trim()),
            Department : data.Department,
            ResidenceBuildingName : data.BuildingName,
            AdultFamilyMembers : data.AdultFamilyMembers,
            NoofChildren : data.NoofChildren,
            campusname : request.user.campusname
        });  
        await doc.assignFacultyID();

        response.send({
            success: true,
            message: 'saved successfully'
        }); 

    }catch(err){ return next(new ErrorResponse(err, 400)); }
};

exports.residenceBuildNameAddFacultyDetails = async (request, response, next) => {
    try{
        let allResidenceBuildings = await CampusBuilding.find({BuildingType: "Faculty Residence", campusname : request.user.campusname}, 'BuildingName');
        response.send({
            ResidenceBuildingName: allResidenceBuildings
        });
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

exports.deleteFacultyDetails = async (request, response, next) => {
    try {
        const { FacultyID } = request.query;
        await Faculty.findByIdAndDelete(FacultyID);
        response.send({
            success: true,
            message: 'deleted successfully'
        });
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

/****************************************************************/

exports.staffDetails = async (request, response, next) => {
    try{
        let viewdata = await Staff.find({campusname : request.user.campusname});
        response.send(viewdata);
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    } 
};

exports.templatestaffdetails = async (request, response, next) => {
    const workbook = new excel.Workbook();
    const filename = "Staff_template";
    const sheet = workbook.addWorksheet(filename);

    sheet.columns = [
        { header: "Staff ID"},
        { header: "Staff Category"},
        { header: "Workplace Building Name"},
        { header: "Residence Building Name"},
        { header: "Adult Family Members"}, 
        { header: "No of Children"}
    ];
  
    response.setHeader(
    "Content-Type",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    );
    response.setHeader(
    "Content-Disposition",
    "attachment; filename=" + filename + ".xlsx"
    );

    return workbook.xlsx.write(response).then(function () {
        response.status(200).end();
    });
};

exports.uploadstaffdetails = async (request, response, next) => {
    try {
        if (request.file == undefined) {
            return next(new ErrorResponse("Please upload an excel file!",400));
        }
        let path = request.file.path;
    
        let rows = await readXlsxFile(path);

        const required_headers = ["Staff ID","Staff Category", "Workplace Building Name", "Residence Building Name", "Adult Family Members", "No of Children"];
        let header = rows.shift();

        for(let i=0; i<required_headers.length; i++){
            if(header[i] != required_headers[i])
                throw "Wrong headers! please match with template file!";
        }
    
        let staffs = [];

        rows.forEach((row) => {
            let staff = {
                StaffID : row[0],
                StaffCategory : row[1],
                WorkplaceBuildingName : row[2],
                ResidenceBuildingName : row[3],
                AdultFamilyMembers : row[4],
                NoofChildren : row[5],
                campusname : request.user.campusname,
            };    
            staffs.push(staff);
        });

        const docs = await Staff.insertMany(staffs);
        if(docs){            
            for(let doc of docs){
                await doc.assignStaffID();
            }
        }

        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        try{
            fs.unlinkSync(request.file.path);
        }catch(err) {
            return next(new ErrorResponse("Could not delete the temp file!(internal err) " + err, 500));
        }
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

exports.addStaffDetails = async (request, response, next) => {
    const data = request.body;
    try{
        const doc = await Staff.create({
            StaffID : data.StaffID,
            StaffCategory : data.StaffCategory,
            WorkplaceBuildingName : data.WorkplaceBuildingName,
            ResidenceBuildingName : data.ResidenceBuildingName,
            AdultFamilyMembers :data.AdultFamilyMembers,
            NoofChildren : data.NoofChildren,
            campusname : request.user.campusname
        });  
        await doc.assignStaffID();

        response.send({
            success: true,
            message: 'saved successfully'
        }); 

    }catch(err){ return next(new ErrorResponse(err, 400)); }
};

exports.deleteStaffDetails = async (request, response, next) => {
    try {
        const { StaffID } = request.query;
        await Staff.findByIdAndDelete(StaffID);
        response.send({
            success: true,
            message: 'deleted successfully'
        });
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

/****************************************************************/
