const fs = require("fs");

exports.home = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};
