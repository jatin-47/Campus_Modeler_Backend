const express = require('express');
const router = express.Router();

const { protect } = require('../middleware/auth');
const { adminprotect } = require('../middleware/admincheck');
const uploadExcel = require("../middleware/uploadExcel");
const uploadImage = require("../middleware/uploadImage");
const uploadJson = require("../middleware/uploadJson");

const { getBatchCodesAddClassClassSchedule, buildingTypes, campusBuildings, viewDataCampusBuildings, templateCampusBuildings, uploadCampusBuildings, uploadspecialrooms, addBuildingCampusBuildings, deleteBuildingCampusBuildings, classSchedule, viewDetailsClassSchedule, deleteClassClassSchedule, templateclassschedule,uploadclassschedule,addClassClassSchedule, getBuildingAddClassClassSchedule, getRoomNameAddClassClassSchedule, getCourseInstructorAddClassClassSchedule, users, viewDetailsUsers,templateusers,uploadusers, addUserUsers, surveyUploader, deleteSurveyUploader, updateSurveyUploader, downloadSurveyUploader, addStudentDataUploader, deleteStudentDataUploader, updateStudentDataUploader, batchwiseStudentDetails,templatebatchwisestudentdetails,uploadbatchwisestudentdetails,uploadbatchwiseDistribution, addBatchwiseStudentDetails, deleteBatchwiseStudentDetails, facultyDetails,templatefacultydetails, uploadfacultydetails,addFacultyDetails, residenceBuildNameAddFacultyDetails, deleteFacultyDetails, staffDetails, templatestaffdetails,uploadstaffdetails,addStaffDetails, deleteStaffDetails } = require('../controllers/masterdata');

router.use(protect);
router.use(adminprotect);
// Protected & admin ONLY Routes from here
router.route('/campusbuildings').get(campusBuildings);
router.route('/campusbuildings/viewdata').get(viewDataCampusBuildings);
router.route('/campusbuildings/template').get(templateCampusBuildings);
router.post('/campusbuildings/upload',uploadExcel.single("file"), uploadCampusBuildings);
router.post('/campusbuildings/upload/specialrooms',uploadJson.single("file"), uploadspecialrooms);
router.route('/campusbuildings/addbuilding').post(addBuildingCampusBuildings);
router.route('/campusbuildings/deletebuilding').delete(deleteBuildingCampusBuildings);
router.route('/campusbuildings/buildingTypes').get(buildingTypes);

router.route('/classschedule').get(classSchedule);
router.route('/classschedule/viewdetails').get(viewDetailsClassSchedule);
router.route('/classschedule/deleteclass').delete(deleteClassClassSchedule);
router.route('/classschedule/template').get(templateclassschedule);
router.post('/classschedule/upload',uploadExcel.single("file"), uploadclassschedule);
router.post('/classschedule/uploadbatchwisecoursedetails',uploadJson.single("file"), uploadbatchwiseDistribution)
router.route('/classschedule/addclass').post(addClassClassSchedule);
router.route('/classschedule/addclass/getbuildingname').get(getBuildingAddClassClassSchedule);
router.route('/classschedule/addclass/getroomName').get(getRoomNameAddClassClassSchedule);
router.route('/classschedule/addclass/getCourseInstructor').get(getCourseInstructorAddClassClassSchedule);
router.route('/classschedule/addclass/getBatchCodes').get(getBatchCodesAddClassClassSchedule);

router.route('/users').get(users);
router.route('/users/viewdetails').get(viewDetailsUsers);
router.route('/users/template').get(templateusers);
router.post('/users/upload', uploadExcel.single("file"), uploadusers);
router.route('/users/adduser').post(addUserUsers);

router.post('/surveyuploader', uploadExcel.single("file") ,surveyUploader);
router.route('/surveyuploader/delete').delete(deleteSurveyUploader);
router.patch('/surveyuploader/update', uploadExcel.single("file") ,updateSurveyUploader);
router.route('/surveyuploader/download').get(downloadSurveyUploader);

router.post('/studentdatauploader/add', uploadExcel.single("file"),addStudentDataUploader);
router.route('/studentdatauploader/delete').delete(deleteStudentDataUploader);
router.patch('/studentdatauploader/update', uploadExcel.single("file"),updateStudentDataUploader);

router.route('/batchwisestudentdetails').get(batchwiseStudentDetails);
router.route('/batchwisestudentdetails/template').get(templatebatchwisestudentdetails);
router.post('/batchwisestudentdetails/upload',uploadExcel.single("file"), uploadbatchwisestudentdetails);
router.route('/batchwisestudentdetails/add').post(addBatchwiseStudentDetails);
router.route('/batchwisestudentdetails/delete').delete(deleteBatchwiseStudentDetails);

router.route('/facultydetails').get(facultyDetails);
router.route('/facultydetails/template').get(templatefacultydetails);
router.post('/facultydetails/upload',uploadExcel.single("file"), uploadfacultydetails);
router.route('/facultydetails/add').post(addFacultyDetails);
router.route('/facultydetails/add/residencebuildname').get(residenceBuildNameAddFacultyDetails);
router.route('/facultydetails/delete').delete(deleteFacultyDetails);

router.route('/staffdetails').get(staffDetails);
router.route('/staffdetails/template').get(templatestaffdetails);
router.post('/staffdetails/upload',uploadExcel.single("file"), uploadstaffdetails);
router.route('/staffdetails/add').post(addStaffDetails);
router.route('/staffdetails/delete').delete(deleteStaffDetails);


module.exports = router;
