const express = require('express');
const router = express.Router();

const { temp } = require('../controllers/main');

router.route('/campusbuildings').get(temp);
router.route('/campusbuildings/viewdata').get(temp);
router.route('/campusbuildings/upload').get(temp);
router.route('/campusbuildings/addbuilding').get(temp);
router.route('/campusbuildings/deletebuilding').delete(temp);
router.route('/classschedule').get(temp);
router.route('/classschedule/viewdetails').get(temp);
router.route('/classschedule/deleteclass').get(temp);
router.route('/classschedule/addclass').get(temp);
router.route('/classschedule/addclass/getbuildingname').get(temp);
router.route('/classschedule/addclass/getroomid').get(temp);
router.route('/classschedule/addclass/getStudentStrength').get(temp);
router.route('/classschedule/addclass/getCourseInstructor').get(temp);
router.route('/classschedule/addclass/addStudentComposition').get(temp);
router.route('/classschedule/addclass/editStudentComposition').get(temp);
router.route('/classschedule/addclass/deleteStudentComposition').get(temp);
router.route('/users').get(temp);
router.route('/users/viewdetails').get(temp);
router.route('/users/adduser').get(temp);
router.route('/surveyuploader').get(temp);
router.route('/surveyuploader/delete').get(temp);
router.route('/surveyuploader/update').get(temp);
router.route('/surveyuploader/download').get(temp);
router.route('/campusmapuploader/add').get(temp);
router.route('/campusmapuploader/update').get(temp);
router.route('/studentdatauploader/add').get(temp);
router.route('/studentdatauploader/delete').get(temp);
router.route('/studentdatauploader/update').get(temp);
router.route('/batchwisestudentdetails').get(temp);
router.route('/batchwisestudentdetails/add').get(temp);
router.route('/batchwisestudentdetails/delete').get(temp);
router.route('/facultydetails').get(temp);
router.route('/facultydetails/add').get(temp);
router.route('/facultydetails/add/residencebuildname').get(temp);
router.route('/facultydetails/delete').get(temp);
router.route('/staffdetails').get(temp);
router.route('/staffdetails/add').get(temp);
router.route('/staffdetails/delete').get(temp);



// router.route('/upload').get(upload).post(uploadMiddleware.single('file'), upload);
// router.route('/blog').get(blog);
// router.route('/projects').post(projects);


module.exports = router;
