// Third party imports
require('dotenv').config({ path: './config.env' });
const express = require('express');
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const cors = require('cors');


// node inbuilt package imports
const path = require('path');

// filesystem imports
const connectDB = require('./config/db');
const errorHandler = require('./middleware/error');
const User = require('./models/User');
// const models = require('./models'); // import all the models


// Connecting to Database
connectDB();


// Creating an express app
const app = express();

global.__basedir = __dirname;

const corsOptions = {
    "origin": ['http://localhost:3000'],
    "methods": "GET,HEAD,PUT,PATCH,POST,DELETE",
    "preflightContinue": false,
    "optionsSuccessStatus": 204,
    "credentials": true
}

// Configuring cors
app.use(cors(corsOptions));

// Adding a json middleware for parsing application/json data
app.use(express.json());
// For parsing application/xwww-form-urlencoded data
app.use(bodyParser.urlencoded({ extended: true }));
// For parsing multipart/form-data
// app.use(upload.array());

// Setting port as a key 'port' to the app
app.set('port', process.env.PORT || 5050);

// Setting up the routes
app.get('/', (request, response) => {
    response.send('Hello World');
});
app.use('/campus/main', require('./routes/main'));
app.use('/campus/simulation', require('./routes/simulation'));
app.use('/campus/masterdata', require('./routes/masterdata'));
app.use('/campus/campussimulator', require('./routes/campus_simulator'));
// app.use('/admin', require('./routes/admin/index'));


// 404 middleware
app.use((request, response, next) => {
    response.status(404)
        .send("Oops! The page you are looking for doesn't exist");
    next();
});

app.use(errorHandler);

// Listening at the port set before
app.listen(app.get('port'), () => {
    // Loggin the server host name and port
    console.log(`Server Running at http://${(process.env.NODE_ENV === 'production') ? '172.105.49.237' : 'localhost'}:${app.get('port')}/`)
});

process.on('unhandledRejection', (error, promise) => {
    console.log(`Logged Error: ${error}`);
    server.close(() => { process.exit(1) });
});

