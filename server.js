require('dotenv').config({ path: './config.env' });
const express = require('express');
const cors = require('cors');

const connectDB = require('./config/db');
const errorHandler = require('./middleware/error');
const {protect} = require('./middleware/auth');
const {adminprotect} = require('./middleware/admincheck');

// const createuser = require('./create_user');
// createuser("Kartheek", "kartheek@gmail.com", "123456", "admin", "IIT Jodhpur", "Kartheek", "Vajrala", "Male");

// const Counter = require("./models/Counter");
// const CampusNames = require('./config/campusnames');
// for(let campus of CampusNames.enum){
//     Counter.create({
//         campusname : campus
//     });
// } 

connectDB();

const app = express();

global.__basedir = __dirname;

const corsOptions = {
    "origin": ['http://localhost:3000', 'http://65.0.60.100', 'http://campusmodeler.ihub-drishti.ai/', 'https://campusmodeler.ihub-drishti.ai/'],
    "methods": "GET,HEAD,PUT,PATCH,POST,DELETE",
    "preflightContinue": false,
    "optionsSuccessStatus": 204,
    "credentials": true
}
app.use(cors(corsOptions));

// Adding a json middleware for parsing application/json data
app.use(express.json());
// For parsing application/xwww-form-urlencoded data
app.use(express.urlencoded({ extended: true }));

// Setting port as a key 'port' to the app
app.set('port', process.env.PORT || 5050);


// Setting up the routes
app.get('/', (request, response) => {
    response.send('Hello World');
});
app.use('/static', protect, adminprotect, express.static(process.env.STATIC_PATH));
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
});

