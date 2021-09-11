const User = require('../models/User');
const Campus = require('../models/Campus');
const ErrorResponse = require('../utils/errorResponse');
const fs = require("fs");

exports.login = async (request, response, next) => {

    const { username, password, role, campusname } = request.body;
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
    try {
        const campuses = await Campus.find({}, 'campusname');
        response.send({
            campusname : campuses.map((curr) => curr.campusname)
        });
    }
    catch(err){
        response.send(err);
    }
};


const sendToken = (user, statusCode, response) => {
    const token = user.getSignedToken();
    response.status(statusCode).json({ message: 'Sucessfully Logined', token, role: ['admin', 'user'] });
}