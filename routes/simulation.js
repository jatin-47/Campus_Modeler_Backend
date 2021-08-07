const express = require('express');
const router = express.Router();

const { protect } = require('../middleware/auth')

const { policyPlanner, initialization, saveSimulation, savedSimulations, deleteSavedSimulations, run, save, runSavedSimulations } = require('../controllers/simulation');

router.route('/policyplanner').get(protect, policyPlanner);
router.route('/initialization').get(protect, initialization);
router.route('/savesimulation').get(protect, saveSimulation);
router.route('/savedsimulations').get(protect, savedSimulations);
router.route('/savedsimulations/delete').get(protect, deleteSavedSimulations);
router.route('/run').get(protect, run);
router.route('/save').get(protect, save);
router.route('/savedsimulations/run').get(protect, runSavedSimulations);

// router.route('/upload').get(upload).post(uploadMiddleware.single('file'), upload);
// router.route('/blog').get(blog);
// router.route('/projects').post(projects);


module.exports = router;