const express = require('express');
const router = express.Router();

const { protect } = require('../middleware/auth')

const { campusBuildings, viewDataCampusBuildings, uploadCampusBuildings, addBuildingCampusBuildings, deleteBuildingCampusBuildings, classSchedule, viewDetailsClassSchedule, deleteClassClassSchedule, addClassClassSchedule, getBuildingAddClassClassSchedule, getRoomIdAddClassClassSchedule, getStudentStrengthAddClassClassSchedule, getCourseInstructorAddClassClassSchedule, addStudentCompositionAddClassClassSchedule, editStudentCompositionAddClassClassSchedule, deleteStudentCompositionAddClassClassSchedule, users, viewDetailsUsers, addUserUsers, surveyUploader, deleteSurveyUploader, updateSurveyUploader, downloadSurveyUploader, addCampusMapUploader, updateCampusMapUploader, addStudentDataUploader, deleteStudentDataUploader, updateStudentDataUploader, batchwiseStudentDetails, addBatchwiseStudentDetails, deleteBatchwiseStudentDetails, facultyDetails, addFacultyDetails, residenceBuildNameAddFacultyDetails, deleteFacultyDetails, staffDetails, addStaffDetails, deleteStaffDetails } = require('../controllers/masterdata');

router.use(protect);
// Protected Routes from here
router.route('/campusbuildings').get(campusBuildings);
router.route('/campusbuildings/viewdata').get(viewDataCampusBuildings);
router.route('/campusbuildings/upload').post(uploadCampusBuildings);
router.route('/campusbuildings/addbuilding').post(addBuildingCampusBuildings);
router.route('/campusbuildings/deletebuilding').delete(deleteBuildingCampusBuildings);
router.route('/classschedule').get(classSchedule);
router.route('/classschedule/viewdetails').get(viewDetailsClassSchedule);
router.route('/classschedule/deleteclass').delete(deleteClassClassSchedule);
router.route('/classschedule/addclass').post(addClassClassSchedule);
router.route('/classschedule/addclass/getbuildingname').get(getBuildingAddClassClassSchedule);
router.route('/classschedule/addclass/getroomid').get(getRoomIdAddClassClassSchedule);
router.route('/classschedule/addclass/getStudentStrength').get(getStudentStrengthAddClassClassSchedule);
router.route('/classschedule/addclass/getCourseInstructor').get(getCourseInstructorAddClassClassSchedule);
router.route('/classschedule/addclass/addStudentComposition').post(addStudentCompositionAddClassClassSchedule);
router.route('/classschedule/addclass/editStudentComposition').patch(editStudentCompositionAddClassClassSchedule);
router.route('/classschedule/addclass/deleteStudentComposition').delete(deleteStudentCompositionAddClassClassSchedule);
router.route('/users').get(users);
router.route('/users/viewdetails').get(viewDetailsUsers);
router.route('/users/adduser').post(addUserUsers);
router.route('/surveyuploader').post(surveyUploader);
router.route('/surveyuploader/delete').delete(deleteSurveyUploader);
router.route('/surveyuploader/update').patch(updateSurveyUploader);
router.route('/surveyuploader/download').get(downloadSurveyUploader);
router.route('/campusmapuploader/add').post(addCampusMapUploader);
router.route('/campusmapuploader/update').patch(updateCampusMapUploader);
router.route('/studentdatauploader/add').post(addStudentDataUploader);
router.route('/studentdatauploader/delete').delete(deleteStudentDataUploader);
router.route('/studentdatauploader/update').patch(updateStudentDataUploader);
router.route('/batchwisestudentdetails').get(batchwiseStudentDetails);
router.route('/batchwisestudentdetails/add').post(addBatchwiseStudentDetails);
router.route('/batchwisestudentdetails/delete').delete(deleteBatchwiseStudentDetails);
router.route('/facultydetails').get(facultyDetails);
router.route('/facultydetails/add').post(addFacultyDetails);
router.route('/facultydetails/add/residencebuildname').get(residenceBuildNameAddFacultyDetails);
router.route('/facultydetails/delete').delete(deleteFacultyDetails);
router.route('/staffdetails').get(staffDetails);
router.route('/staffdetails/add').post(addStaffDetails);
router.route('/staffdetails/delete').delete(deleteStaffDetails);


module.exports = router;
