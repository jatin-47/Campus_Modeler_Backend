const User = require('../models/User');
const ErrorResponse = require('../utils/errorResponse');

exports.adminprotect = async (request, response, next) => {
    const user = request.user;
    if(user.role == "admin"){       
        next();
    }
    else{
        return next(new ErrorResponse("Not authorized to access this route (Only admins)!", 401));
    }
}