const express = require('express');
const router = express.Router();

const { login, campusName } = require('../controllers/main');

router.route('/login').get(login);
router.route('/campusname').get(campusName);
// router.route('/upload').get(upload).post(uploadMiddleware.single('file'), upload);
// router.route('/blog').get(blog);
// router.route('/projects').post(projects);


module.exports = router;