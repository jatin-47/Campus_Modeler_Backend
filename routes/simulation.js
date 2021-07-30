const express = require('express');
const router = express.Router();

const { temp } = require('../controllers/main');

router.route('/initialization').get(temp);
router.route('/savesimulation').get(temp);
router.route('/savedsimulations').get(temp);
router.route('/savedsimulations/delete').get(temp);
router.route('/run').get(temp);
router.route('/save').get(temp);
router.route('/savedsimulations/run').get(temp);

// router.route('/upload').get(upload).post(uploadMiddleware.single('file'), upload);
// router.route('/blog').get(blog);
// router.route('/projects').post(projects);


module.exports = router;