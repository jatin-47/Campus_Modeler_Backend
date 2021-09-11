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
router.route('/users/adduser').get(addUserUsers);
router.route('/surveyuploader').get(surveyUploader);
router.route('/surveyuploader/delete').get(deleteSurveyUploader);
router.route('/surveyuploader/update').get(updateSurveyUploader);
router.route('/surveyuploader/download').get(downloadSurveyUploader);
router.route('/campusmapuploader/add').get(addCampusMapUploader);
router.route('/campusmapuploader/update').get(updateCampusMapUploader);
router.route('/studentdatauploader/add').get(addStudentDataUploader);
router.route('/studentdatauploader/delete').get(deleteStudentDataUploader);
router.route('/studentdatauploader/update').get(updateStudentDataUploader);
router.route('/batchwisestudentdetails').get(batchwiseStudentDetails);
router.route('/batchwisestudentdetails/add').get(addBatchwiseStudentDetails);
router.route('/batchwisestudentdetails/delete').get(deleteBatchwiseStudentDetails);
router.route('/facultydetails').get(facultyDetails);
router.route('/facultydetails/add').get(addFacultyDetails);
router.route('/facultydetails/add/residencebuildname').get(residenceBuildNameAddFacultyDetails);
router.route('/facultydetails/delete').get(deleteFacultyDetails);
router.route('/staffdetails').get(staffDetails);
router.route('/staffdetails/add').get(addStaffDetails);
router.route('/staffdetails/delete').get(deleteStaffDetails);



// router.route('/upload').get(upload).post(uploadMiddleware.single('file'), upload);
// router.route('/blog').get(blog);
// router.route('/projects').post(projects);


module.exports = router;
