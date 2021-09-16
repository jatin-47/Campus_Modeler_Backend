const User = require('../models/User');
const CampusBuilding = require('../models/CampusBuilding');
const ClassSchedule = require('../models/ClassSchedule');
const BatchStudent = require('../models/BatchStudent');
const Faculty = require('../models/Faculty');
const Staff = require('../models/Staff');
const Survey = require('../models/Survey');
const StudentData = require('../models/StudentData');
const Counter = require('../models/Counter');

const ErrorResponse = require('../utils/errorResponse');
var fs = require('fs');
const PATH = require('path');
const readXlsxFile = require('read-excel-file/node');
const excel = require("exceljs");

/****************************************************************/

exports.campusBuildings = async (request, response, next) => {

    let CampusBuildings = await CampusBuilding.find({campusname : request.user.campusname}, 'BuildingID BuildingName BuildingType NoOfFloors NoOfWorkers Status');

    response.send(CampusBuildings);
};

exports.viewDataCampusBuildings = async (request, response, next) => {

    const { BuildingID } = request.query;
    try {
        let viewdata = await CampusBuilding.findOne({ campusname : request.user.campusname, BuildingID: BuildingID });
        if(viewdata)
            response.send(viewdata);
        else
            return next(new ErrorResponse('Not Found',400));
    }catch(err){  return next(new ErrorResponse(err,400));  }

};

exports.templateCampusBuildings = async (request, response, next) => {
    const workbook = new excel.Workbook();
    const filename = "building_template";
    const sheet = workbook.addWorksheet(filename);

    sheet.columns = [
        { header: "Building Name"},
        { header: "Building Type"},
        { header: "Building Status"},
        { header: "Number of Floors"},
        { header: "Number of Rooms in Each Floor"},
        { header: "Number of Workers"},
        { header: "Active Hours"},
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
        //console.log(request.file);
        let path = request.file.path;
    
        let rows = await readXlsxFile(path);

        const required_headers = ["Building Name","Building Type","Building Status","Number of Floors", 
        "Number of Rooms in Each Floor", "Number of Workers","Active Hours","Building Polygon"];
        let header = rows.shift();

        for(let i=0; i<required_headers.length; i++){
            if(header[i] != required_headers[i])
                throw "Wrong headers! please match with template file!";
        }
    
        let buildings = [];
    
        rows.forEach((row) => {
            let building = {
                BuildingID : row[0],
                BuildingName : row[1],
                BuildingType : row[2],
                NoOfFloors : row[3],
                NoOfWorkers : row[4],
                Status : row[5] , 
                ActiveHours : row[6],
                BuildingCordinaties : row[7],
                campusname : request.user.campusname,
                Rooms : []
            };
            let start_col = 8;
            for(let i=0; i<TotalNoOfRooms; i++)
            {
                let room = {
                    RoomID : row[start_col],
                    RoomName : row[start_col+1],
                    Floor : row[start_col+2],
                    Capacity : row[start_col+3],
                    RoomType : row[start_col+4]
                };
                building.Rooms.push(room);
                start_col = start_col+5;
            }
    
            buildings.push(building);
        });

        await CampusBuilding.insertMany(buildings);

        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        fs.unlinkSync(request.file.path);
        console.log(error);
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

//RoomID logic `BuildingID + FloorNo + RoomNo`
exports.addBuildingCampusBuildings = async (request, response, next) => {
    const data = request.body;
    try {
        const floors = data.RoomDetails;
        let Rooms = []
    
        for(let floor of floors){
            for(let i =0; i<floor.NumberofRooms; i++){
                let room = {
                    RoomID : `${data.BuildingId}${floor.FloorNo}${i}`, //RoomID LOGIC
                    RoomName : floor.Rooms[i].RoomName, 
                    Floor : floor.FloorNo, 
                    Capacity : floor.Rooms[i].Capacity, 
                    RoomType : floor.Rooms[i].RoomType
                };
                Rooms.push(room);
            }
        }
        await CampusBuilding.create({ 
            BuildingID : data.BuildingId,
            BuildingName : data.BuildingName,
            BuildingType : data.BuildingType,
            NoOfFloors : data.NoOfFloors,
            NoOfWorkers : data.NoOfWorkers,
            ActiveHours : {
                start : data.ActiveHours[0],
                end : data.ActiveHours[1] 
            },
            BuildingCordinaties :data.BuildingCordinaties,
            campusname : request.user.campusname,
            Rooms : Rooms
        });
    
        response.send({
            success: true,
            message: 'saved successfully'
        });
    }
    catch(err){
        return next(new ErrorResponse(err,400));
    }
};

exports.deleteBuildingCampusBuildings = async (request, response, next) => {
    try {
        const { BuildingID } = request.query;
        await CampusBuilding.deleteOne({ campusname : request.user.campusname, BuildingID : BuildingID})
    
        response.send({
            success: true,
            message: 'deleted successfully'
        });

    } catch(err){  return next(new ErrorResponse(err,400));  }
};

/****************************************************************/

exports.classSchedule = async (request, response, next) => {

    try{
        let ClassSchedules = await ClassSchedule.find({campusname : request.user.campusname}, 'CourseID CourseName RoomID Strength Departments Status');
        //roomid from its objectid
    
        response.send(ClassSchedules);
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

exports.viewDetailsClassSchedule = async (request, response, next) => {

    const { CourseID } = request.query;
    try{
        let viewdata = await ClassSchedule.findOne({ campusname : request.user.campusname, CourseID: CourseID });
        response.send(viewdata);
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

exports.deleteClassClassSchedule = async (request, response, next) => {
    const { CourseID } = request.query;
    try {
        await ClassSchedule.deleteOne({ campusname : request.user.campusname, CourseID : CourseID})
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
        { header: "Room ID"},
        { header: "Scheduled Days"},
        { header: "Scheduled Time"},
        { header: "Total Strength"}
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
        //console.log(request.file);
        let path = request.file.path;
    
        let rows = await readXlsxFile(path);

        const required_headers = [ /* headers list to be pasted from template*/];
        let header = rows.shift();

        for(let i=0; i<required_headers.length; i++){
            if(header[i] != required_headers[i])
                throw "Wrong headers! please match with template file!";
        }
    
        /* let buildings = [];
    
        rows.forEach((row) => {
            let building = {
                BuildingID : row[0],
                BuildingName : row[1],
                BuildingType : row[2],
                NoOfFloors : row[3],
                NoOfWorkers : row[4],
                Status : row[5] , 
                ActiveHours : row[6],
                BuildingCordinaties : row[7],
                campusname : request.user.campusname,
                Rooms : []
            };
            let start_col = 8;
            for(let i=0; i<TotalNoOfRooms; i++)
            {
                let room = {
                    RoomID : row[start_col],
                    RoomName : row[start_col+1],
                    Floor : row[start_col+2],
                    Capacity : row[start_col+3],
                    RoomType : row[start_col+4]
                };
                building.Rooms.push(room);
                start_col = start_col+5;
            }
    
            buildings.push(building);
        });

        await CampusBuilding.insertMany(buildings);
 */
        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        fs.unlinkSync(request.file.path);
        console.log(error);
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

exports.addClassClassSchedule = async (request, response, next) => {
    const data = request.body;

    try{
        const building = await CampusBuilding.findOne({campusname : request.user.campusname, BuildingName:data.BuildingName});
        if(!building) throw "No such building found in which this class is scheduled!";
        const room = building.Rooms.filter((curr)=> curr.RoomID==data.RoomID); 
        if(room.length == 0) throw "No such room found in which this class is scheduled!";
    
        await ClassSchedule.create({
            CourseID : data.CourseID,
            CourseName : data.CourseName,
            RoomID :room[0]._id,
            BuildingName : building._id,
            Strength : data.Strength,
            Departments : data.Departments,
            Status : true,
            ClassDays : data.ClassDays.map((curr) => { curr.Timing = {start: curr.Timing[0], end: curr.Timing[1]}; return curr} ),
            CourseInstructor : data.CourseInstructor,
            StudentComposition : data.StudentComposition,
            campusname : request.user.campusname
        });   
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
    response.send({
        success: true,
        message: 'saved successfully'
    });
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
    const { BuildingId } = request.query;
    try{
        if(BuildingId) {
            const building = await CampusBuilding.findOne({campusname : request.user.campusname,BuildingID : BuildingId}, 'Rooms');
            response.send(building);
        }
        else {
            const building = await CampusBuilding.findOne({campusname : request.user.campusname}, 'Rooms');
            response.send(building);
        }
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }

};

exports.getStudentStrengthAddClassClassSchedule = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.getCourseInstructorAddClassClassSchedule = async (request, response, next) => {
    try {
        let faculties = await Faculty.find({campusname : request.user.campusname}, 'Name');
        response.send(faculties);
    }
    catch(err){  return next(new ErrorResponse(err,400));  }
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

/****************************************************************/

//add "UserID" column also after counter work is done
exports.users = async (request, response, next) => {

    try{
        let viewdata = await User.find({campusname : request.user.campusname}, 'username role email contact status');
        response.send(viewdata);
    }catch(err){ return next(new ErrorResponse(err, 400)); }   
    
};

//ask how the UI is taking the image!!
exports.viewDetailsUsers = async (request, response, next) => {
    const { UserID } = request.query;
    try{
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

//add "UserID" column also after counter work is done 
//uniqueness validation not available!
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
                const campusCounter = await Counter.findOne({campusname: doc.campusname});
                doc.UserID = await campusCounter.increaseCount("User"); 
                await doc.save();
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
        //console.log(error);
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

//add "UserID" column also after counter work is done 
exports.addUserUsers = async (request, response, next) => {
    const data = request.body;
    let path = request.file.path;
    try{
        await User.create({
            username: data.Username,
            email: data.Email,
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
    if (request.file == undefined) {
        return next(new ErrorResponse("Please upload an excel file!",400));
    }
    try {      
        
        
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
        { header: "Batch_Code"},
        { header: "YearofStudy"},
        { header: "Department_Code"},
        { header: "Program_Code"},
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
        //console.log(request.file);
        let path = request.file.path;
    
        let rows = await readXlsxFile(path);

        const required_headers = [ /* headers list to be pasted from template*/];
        let header = rows.shift();

        for(let i=0; i<required_headers.length; i++){
            if(header[i] != required_headers[i])
                throw "Wrong headers! please match with template file!";
        }
    
        /* let buildings = [];
    
        rows.forEach((row) => {
            let building = {
                BuildingID : row[0],
                BuildingName : row[1],
                BuildingType : row[2],
                NoOfFloors : row[3],
                NoOfWorkers : row[4],
                Status : row[5] , 
                ActiveHours : row[6],
                BuildingCordinaties : row[7],
                campusname : request.user.campusname,
                Rooms : []
            };
            let start_col = 8;
            for(let i=0; i<TotalNoOfRooms; i++)
            {
                let room = {
                    RoomID : row[start_col],
                    RoomName : row[start_col+1],
                    Floor : row[start_col+2],
                    Capacity : row[start_col+3],
                    RoomType : row[start_col+4]
                };
                building.Rooms.push(room);
                start_col = start_col+5;
            }
    
            buildings.push(building);
        });

        await CampusBuilding.insertMany(buildings);
 */
        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        fs.unlinkSync(request.file.path);
        console.log(error);
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

exports.addBatchwiseStudentDetails = async (request, response, next) => {
    const data = request.body;
    try{
        await BatchStudent.create({
            BatchCode : data.BatchCode,
            Department : data.Department,
            ProgramCode : data.ProgramCode,
            YearOfStudy : data.YearOfStudy,
            Strength : data.Strength,
            campusname : request.user.campusname
        });  

        response.send({
            success: true,
            message: 'saved successfully'
        }); 

    }catch(err){ return next(new ErrorResponse(err, 400)); }
};

exports.deleteBatchwiseStudentDetails = async (request, response, next) => {
    const { BatchID } = request.query;
    try {
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
        { header: "Courses"},
        { header: "Department_Code"},
        { header: "ResidenceBuildingName"},
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
        //console.log(request.file);
        let path = request.file.path;
    
        let rows = await readXlsxFile(path);

        const required_headers = [ /* headers list to be pasted from template*/];
        let header = rows.shift();

        for(let i=0; i<required_headers.length; i++){
            if(header[i] != required_headers[i])
                throw "Wrong headers! please match with template file!";
        }
    
        /* let buildings = [];
    
        rows.forEach((row) => {
            let building = {
                BuildingID : row[0],
                BuildingName : row[1],
                BuildingType : row[2],
                NoOfFloors : row[3],
                NoOfWorkers : row[4],
                Status : row[5] , 
                ActiveHours : row[6],
                BuildingCordinaties : row[7],
                campusname : request.user.campusname,
                Rooms : []
            };
            let start_col = 8;
            for(let i=0; i<TotalNoOfRooms; i++)
            {
                let room = {
                    RoomID : row[start_col],
                    RoomName : row[start_col+1],
                    Floor : row[start_col+2],
                    Capacity : row[start_col+3],
                    RoomType : row[start_col+4]
                };
                building.Rooms.push(room);
                start_col = start_col+5;
            }
    
            buildings.push(building);
        });

        await CampusBuilding.insertMany(buildings);
 */
        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        fs.unlinkSync(request.file.path);
        console.log(error);
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

exports.addFacultyDetails = async (request, response, next) => {
    const data = request.body;
    try{
        await Faculty.create({
            Courses : data.Courses,
            Department : data.Department,
            ResidenceBuildingName : data.ResidenceBuildingName,
            AdultFamilyMembers : data.AdultFamilyMembers,
            NoofChildren : data.NoofChildren,
            campusname : request.user.campusname
        });  

        response.send({
            success: true,
            message: 'saved successfully'
        }); 

    }catch(err){ return next(new ErrorResponse(err, 400)); }
};

exports.residenceBuildNameAddFacultyDetails = async (request, response, next) => {
    try{
        let allResidenceBuildings = await Faculty.distinct('ResidenceBuildingName');
        response.send({
            ResidenceBuildingName: allResidenceBuildings
        });
    }
    catch(err){
        return next(new ErrorResponse(err, 400));
    }
};

exports.deleteFacultyDetails = async (request, response, next) => {
    const { FacultyID } = request.query;
    try {
        await BatchStudent.findByIdAndDelete(FacultyID);
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
    const filename = "Faculty_template";
    const sheet = workbook.addWorksheet(filename);

    sheet.columns = [
        { header: "Name"}
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
        //console.log(request.file);
        let path = request.file.path;
    
        let rows = await readXlsxFile(path);

        const required_headers = [ /* headers list to be pasted from template*/];
        let header = rows.shift();

        for(let i=0; i<required_headers.length; i++){
            if(header[i] != required_headers[i])
                throw "Wrong headers! please match with template file!";
        }
    
        /* let buildings = [];
    
        rows.forEach((row) => {
            let building = {
                BuildingID : row[0],
                BuildingName : row[1],
                BuildingType : row[2],
                NoOfFloors : row[3],
                NoOfWorkers : row[4],
                Status : row[5] , 
                ActiveHours : row[6],
                BuildingCordinaties : row[7],
                campusname : request.user.campusname,
                Rooms : []
            };
            let start_col = 8;
            for(let i=0; i<TotalNoOfRooms; i++)
            {
                let room = {
                    RoomID : row[start_col],
                    RoomName : row[start_col+1],
                    Floor : row[start_col+2],
                    Capacity : row[start_col+3],
                    RoomType : row[start_col+4]
                };
                building.Rooms.push(room);
                start_col = start_col+5;
            }
    
            buildings.push(building);
        });

        await CampusBuilding.insertMany(buildings);
 */
        fs.unlinkSync(path);
        response.status(200).send({
            success: true,
            message: "Uploaded the file/data successfully!"
        });

    } catch (error) {
        fs.unlinkSync(request.file.path);
        console.log(error);
        return next(new ErrorResponse("Could not upload the file! " + error, 500));
    }
};

exports.addStaffDetails = async (request, response, next) => {
    const data = request.body;
    try{
        await Staff.create({
            StaffCategory : data.StaffCategory,
            WorkplaceBuildingName : data.WorkplaceBuildingName,
            ResidenceBuildingName : data.ResidenceBuildingName,
            AdultFamilyMembers :data.AdultFamilyMembers,
            NoofChildren : data.NoofChildren,
            campusname : request.user.campusname
        });  

        response.send({
            success: true,
            message: 'saved successfully'
        }); 

    }catch(err){ return next(new ErrorResponse(err, 400)); }
};

exports.deleteStaffDetails = async (request, response, next) => {
    const { StaffID } = request.query;
    try {
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
