const express = require('express');
const router = express.Router();

const { login,  logout, campusName } = require('../controllers/main');

router.route('/login').post(login);
router.route('/campusname').get(campusName);

// router.route('/logout').post(logout);

module.exports = router;