const express = require('express');
const router = express.Router();

const { protect } = require('../middleware/auth')

const { campusCoordinates, policyPlanner, initialization, saveSimulation, savedSimulations, deleteSavedSimulations, run, save } = require('../controllers/simulation');


router.use(protect);
// Protected Routes from here
router.route('/campusCoordinates').get(campusCoordinates);
router.route('/policyplanner').get(policyPlanner);
router.route('/initialization').get(initialization);
router.route('/savesimulation').post(saveSimulation);
router.route('/savedsimulations').get(savedSimulations);
router.route('/savedsimulations/delete').delete(deleteSavedSimulations);
router.route('/run').post(run);
router.route('/save').post(save);

// router.route('/savedsimulations/run').get(protect, runSavedSimulations);


module.exports = router;