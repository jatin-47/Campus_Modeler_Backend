const express = require('express');
const router = express.Router();

const { home } = require('../controllers/main');

router.route('/').get(home);
// router.route('/upload').get(upload).post(uploadMiddleware.single('file'), upload);
// router.route('/blog').get(blog);
// router.route('/projects').post(projects);


module.exports = router;