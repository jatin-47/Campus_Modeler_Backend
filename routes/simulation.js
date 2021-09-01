const express = require('express');
const router = express.Router();

const { protect } = require('../middleware/auth')

const { policyPlanner, initialization, saveSimulation, savedSimulations, deleteSavedSimulations, run, save, runSavedSimulations } = require('../controllers/simulation');

router.use(protect);
router.route('/policyplanner').get(policyPlanner);
router.route('/initialization').get(initialization);
router.route('/savesimulation').get(saveSimulation);
router.route('/savedsimulations').get(savedSimulations);
router.route('/savedsimulations/delete').delete(deleteSavedSimulations);
router.route('/run').post(run);
router.route('/save').post(save);

// router.route('/savedsimulations/run').get(protect, runSavedSimulations);
// router.route('/upload').get(upload).post(uploadMiddleware.single('file'), upload);
// router.route('/blog').get(blog);
// router.route('/projects').post(projects);


module.exports = router;