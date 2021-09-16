const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');

const ErrorResponse = require('../utils/errorResponse');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const UserSchema = new mongoose.Schema({
    UserID : {type : Number},
    username: {
        type: String,
        unique: true,
        trim : true,
        required: [true, "Username cannot be empty!"]
    },
    email: {
        type: String,
        required: [true, "Please provide an email"],
        lowercase: true,
        trim : true,
        unique : true,
        match: [
            /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/,
            "Please provide a valid email"
        ]
    },
    password: {
        type: String,
        required: [true, "Please add a password"],
        minlength: 6,
        select: false
    },
    role: { 
        type: String, 
        enum: ['admin', 'user'],
        default: 'user'
    },
    campusname: CampusNames,
    status : {type: Boolean, default:true},
    fname : { type: String, trim : true, required: true},
    lname : { type: String, trim : true, required: true},
    gender : { type: String, required: true, enum: ["Male", "Female", "Others"]},
    contact : { type : Number, min : 1000000000, max : 9999999999},
    dob : { type: String },
    photo_path : { type: String , select: false}
});

UserSchema.pre('save', async function (next) {
    if (!this.isModified('password')) {
        next();
    } else {
        const salt = await bcrypt.genSalt(10);
        this.password = await bcrypt.hash(this.password, salt);
        next();
    }
});

UserSchema.pre('insertMany', async function (next, docs) {
    try{
        tobeEmails = [];
        for(let doc of docs){
            const salt = await bcrypt.genSalt(10);
            doc.password = await bcrypt.hash(doc.password, salt);
            
            let proposedName = (doc.fname + doc.lname + doc.contact.toString().slice(6) + Math.floor((Math.random() * 100) + 1)).replace(/\s/g, '');
            doc.username = await doc.generateUniqueUserName(proposedName.toLowerCase());  
            
            let isUniqueEmail = await doc.isUniqueEmail();
            if(!isUniqueEmail) {
                throw "One or more emails are already used in the database!"
            }
            tobeEmails.push(doc.email);
        }
        if((new Set(tobeEmails)).size !== tobeEmails.length) {
            throw "Your upload contains duplicate emails for two or more users!"
        }
        next();
    } 
    catch (error) {
        return next(new ErrorResponse(error,400));
    }
});

UserSchema.post('remove', async function (next) {
    try{
        const Simulation = require('./Simulation');
        await Simulation.deleteMany({user: this._id});
        next();
    }catch(err){
        return next(new ErrorResponse(err,400));
    }
});

UserSchema.methods.isUniqueEmail = async function () {
    try {
        let user = await User.findOne({email: this.email})
        if(user) {return false;}
        else {return true;}
    } catch(err){
        return err;
    }
}

UserSchema.methods.generateUniqueUserName = async function (proposedName) {
    try {
        let user = await User.findOne({username: proposedName})
        if(user) {
            //console.log('Already exisits: ' + proposedName);
            proposedName += Math.floor((Math.random() * 100) + 1);
            return this.generateUniqueUserName(proposedName); 
        }
        //console.log('proposed name is unique' + proposedName);
        return proposedName;
    }   
    catch(err) {
        //console.error(err);
        return err;
    }
}

UserSchema.methods.matchPassword = async function (password) {
    return await bcrypt.compare(password, this.password);
}

UserSchema.methods.getSignedToken = function () {
    return jwt.sign(
        { id: this._id },
        process.env.JWT_SECRET,
        // { expiresIn: process.env.JWT_EXPIRE }
    );
}


const User = mongoose.model("User", UserSchema);

module.exports = User;