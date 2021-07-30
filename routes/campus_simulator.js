const express = require('express');
const router = express.Router();

const { temp } = require('../controllers/main');

router.route('/visualpanel/peoplecount').get(temp);
router.route('/visualpanel/buildingoccupancy').get(temp);
router.route('/visualpanel/casestatistics').get(temp);
router.route('/visualpanel/peoplelocations').get(temp);


// router.route('/upload').get(upload).post(uploadMiddleware.single('file'), upload);
// router.route('/blog').get(blog);
// router.route('/projects').post(projects);


module.exports = router;
