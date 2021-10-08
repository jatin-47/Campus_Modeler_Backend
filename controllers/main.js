const User = require('../models/User');
const Campus = require('../models/Campus');
const ErrorResponse = require('../utils/errorResponse');

exports.login = async (request, response, next) => {

    const { username, password, campusname } = request.body;
    // console.log(request)
    console.log('Post request');

    if (username && password && campusname) {
        try {
            const user = await User.findOne({ username : username, campusname : campusname}).select('+password');

            if (!user) {
                console.log('Wrong')
                return next(new ErrorResponse("Username not found in given campus", 401));
            }

            const isMatch = await user.matchPassword(password);

            if (!isMatch) {
                return next(new ErrorResponse("Invalid Password", 401));
            }

            sendToken(user, 200, response);

        } catch (error) {
            next(error);
        }
    } else {
        return next(new ErrorResponse("Please provide username, password and campusname", 400));
    }
};

const sendToken = (user, statusCode, response) => {
    const token = user.getSignedToken();
    response.status(statusCode).json({ 
        message: 'Sucessfully Logined', 
        token, 
        role: user.role
    });
}

exports.campusName = async (request, response, next) => {
    try {
        let campuses = await Campus.find({});
        campuses = campuses.map((campus)=>campus.campusname);
        response.send({
            campusname : campuses
        });
    }
    catch(err){  return next(new ErrorResponse(err,400));  }
};


