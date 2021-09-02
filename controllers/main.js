const User = require('../models/User');
const ErrorResponse = require('../utils/errorResponse');
const fs = require("fs");
const runPython = require('../utils/runPython');

exports.login = async (request, response, next) => {

    const { username, password, campusname } = request.body;
    // console.log(request)
    console.log('Post request');
    if (username && password) {
        try {
            const user = await User.findOne({ username }).select("password");

            if (!user) {
                console.log('Wrong')
                return next(new ErrorResponse("Invalid Credentials", 401));
            }

            const isMatch = await user.matchPassword(password);

            if (!isMatch) {
                return next(new ErrorResponse("Invalid Credentials", 401));
            }

            sendToken(user, 200, response);

        } catch (error) {
            next(error);
        }
    } else {
        return next(new ErrorResponse("Please provide username and password", 400));
    }
};


exports.campusName = async (request, response, next) => {
    console.log('Campus Name');
    response.send({
        'campusname': ['madras', 'delhi']
    });
};


const sendToken = (user, statusCode, response) => {
    const token = user.getSignedToken();
    response.status(statusCode).json({ message: 'Sucessfully Logined', token, role: ['admin', 'user'] });
}