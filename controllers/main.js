const User = require('../models/User');

const fs = require("fs");

exports.login = async (request, response, next) => {

    const { username, password, campusname } = request.body;
    // console.log(request)
    console.log('Post request');
    if (username && password) {
        
    } else {
        response.send({
            'hi': 'no'
        });
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