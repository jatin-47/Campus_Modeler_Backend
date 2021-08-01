const express = require('express');
const router = express.Router();

const { login,  logout, campusName } = require('../controllers/main');

router.route('/login').post(login);
router.route('/logout').post(logout);
router.route('/campusname').get(campusName);
// router.route('/upload').get(upload).post(uploadMiddleware.single('file'), upload);
// router.route('/blog').get(blog);
// router.route('/projects').post(projects);


module.exports = router;