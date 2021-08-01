const User = require('../models/User');

const fs = require("fs");

exports.login = async (request, response, next) => {

    const { username, password } = request.body;
    // console.log(request)
    console.log('Post request');
    if (username && password) {
        console.log(username, password)
        try {
            User.findOne({ where: { username } }).then((user) => {
                if (user && user.matchPassword(password)) {
                    request.session.userId = user.id;
                    response.send({
                        'hi': 'loggedin'
                    });
                } else {
                    response.send({
                        'message': 'Invalid Credentials'
                    });
                }
            });
        } catch (error) {
            response.send({
                'hi': error
            });
        }

    } else {
        response.send({
            'hi': 'no'
        });
    }
};


exports.logout = async (request, response, next) => {
    request.session.destroy((error) => {
        if (error) {
            return response.redirect('/admin/dashboard');
        }

        // After destroying the session in the server memory
        // Clear the cookie on client
        response.clearCookie(process.env.SESSION_NAME || 'sid');
        // Then redirect to login page
        response.redirect('/admin/login')
    });
}

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
