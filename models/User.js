const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');

const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const UserSchema = new mongoose.Schema({
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
        for(let doc of docs){
            const salt = await bcrypt.genSalt(10);
            doc.password = await bcrypt.hash(doc.password, salt);
            console.log(doc.password);
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