
exports.isLoggedIn = (request, response, next) => {
    if (!request.session.userId) {
        response.redirect('/admin/login');
    } else {
        next();
    }
};

exports.isNotLoggedIn = (request, response, next) => {
    if (request.session.userId) {
        response.redirect('/admin/dashboard');
    } else {
        next();
    }
};