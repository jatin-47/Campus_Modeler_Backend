const User = require('../models/User');
const ErrorResponse = require('../utils/errorResponse');
const fs = require("fs");

exports.login = async (request, response, next) => {

    const { username, password, campusname } = request.body;
    // console.log(request)
    console.log('Post request');
    if (username && password) {
        try {
            const user = await User.findOne({ username }).select("password");

            if (!user) {
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


exports.logout = async (request, response, next) => {

}

exports.campusName = async (request, response, next) => {

    response.send({
        'campusname': ['madras', 'delhi']
    });
};

exports.temp = async (request, response, next) => {

    response.send({
        'hi': 'temp'
    });
};


const sendToken = (user, statusCode, response) => {
    const token = user.getSignedToken();
    response.status(statusCode).json({ success: true, token });
}