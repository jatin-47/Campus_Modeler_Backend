const User = require('../models/User');

const fs = require("fs");

exports.login = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.campusName = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.temp = async (request, response, next) => {

    response.send({
        'hi': 'temp'
    });
};
