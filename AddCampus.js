const Campus = require("./models/Campus");
const Counter = require('./models/Counter');
const User = require('./models/User');

const prompt = require('prompt');
require('dotenv').config({ path: './config.env' });
const connectDB = require('./config/db');

async function add_campus(){

    let campusschema = {
        properties: {
            campusname: {
                description: 'Campus Name',
                type: 'string',
                pattern: /^[a-zA-Z\s\-]+$/,
                message: 'Name must be only letters, spaces, or dashes',
                required: true
            },
            latitude: {
                description: 'Latitude',
                type: 'number',
                required: true 
            },
            longitude: {
                description: 'Longitude',
                type: 'number',
                required: true 
            }
        }
    };

    let userschema = {
        properties: {
            fname : { 
                description: 'First Name',
                type: 'string',
                required: true
            },
            lname : { 
                description: 'Last Name',
                type: 'string',
                required: true
            },
            username: {
                description: 'User Name',
                type: 'string',
                required: true             
            },
            password: {
                description: 'Password',
                type: 'string',
                minLength: 6,
                message: "Min length should be 6",
                required: true
            },
            email: {
                description: 'Email',
                type: 'string',
                pattern: /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/,
                message: "Please provide a valid email",
                required: true
            },
            gender : { 
                description: 'Gender (Male/Female/Others)',
                type: 'string', 
                enum: ["Male", "Female", "Others"],
                default: 'Male',  
                required: true, 
            },
            contact : {
                description: 'Contact',
                type: 'number',
                minimum : 1000000000, 
                maximum : 9999999999
            },
            dob : {
                description: 'DOB',
                type: 'string'
            }
        }
    };

    try{
        console.log("Connecting to DB...");
        await connectDB();

        prompt.start();

        console.log("\n1. New Campus Details:-\n");
        const newcampus = await prompt.get(campusschema);

        //check if campus already exists!
        let campus = await Campus.findOne({campusname : newcampus.campusname});
        if(campus){
            return onErr("\nThis Campus Name already exists!"); 
        }

        const campus_doc = await Campus.create(newcampus);
        await Counter.create({campusname : campus_doc.campusname});
        console.log(`\nNew Campus created successfully!\n${campus_doc}`);


        console.log(`\n2. New admin User for this campus:-\n`);
        const newuser = await prompt.get(userschema);
        newuser['role'] = "admin";
        newuser['campusname'] = campus_doc.campusname;

        const user_doc = await User.create(newuser);
        await user_doc.assignUserID();
        console.log(`\nNew User created successfully!\n${user_doc}`);
        process.exit(0);
    }
    catch(e){
        return onErr(new Error(e));
    }   
}

add_campus();

function onErr(err) {
    console.error(err);
    process.exit(0);
}