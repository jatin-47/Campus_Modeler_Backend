const express = require('express');
const router = express.Router();

const { initialization, saveSimulation, savedSimulations, deleteSavedSimulations, run, save, runSavedSimulations } = require('../controllers/simulation');

router.route('/initialization').get(initialization);
router.route('/savesimulation').get(saveSimulation);
router.route('/savedsimulations').get(savedSimulations);
router.route('/savedsimulations/delete').get(deleteSavedSimulations);
router.route('/run').get(run);
router.route('/save').get(save);
router.route('/savedsimulations/run').get(runSavedSimulations);

// router.route('/upload').get(upload).post(uploadMiddleware.single('file'), upload);
// router.route('/blog').get(blog);
// router.route('/projects').post(projects);


module.exports = router;