const express = require('express');
const router = express.Router();
const { protect } = require('../middleware/auth');
const { peopleCount, buildingOccupancy, caseStatistics, peopleLocations } = require('../controllers/campus_simulator');

router.use(protect);
// Protected Routes from here
router.route('/visualpanel/peoplecount').get(peopleCount);
router.route('/visualpanel/buildingoccupancy').get(buildingOccupancy);
router.route('/visualpanel/casestatistics').get(caseStatistics);
router.route('/visualpanel/peoplelocations').get(peopleLocations);


// router.route('/upload').get(upload).post(uploadMiddleware.single('file'), upload);
// router.route('/blog').get(blog);
// router.route('/projects').post(projects);


module.exports = router;
