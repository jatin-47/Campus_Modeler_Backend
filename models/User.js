const mongoose = require('mongoose');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const UserSchema = new mongoose.Schema({
    username: {
        type: String,
        unique: true,
        required: [true, "Username cannot be empty!"]
    },
    email: {
        type: String,
        required: [true, "Please provide an email"],
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
        enum: ['admin', 'user'] 
    },
    campusname: {
        type: String,
        enum: ['kharagpur','madras', 'delhi'],
        required: true
    },
    status : {type: Boolean, default:true},
    fname : { type: String, trim : true, required: true},
    lname : { type: String, trim : true, required: true},
    gender : { type: String, required: true, enum: ["Male", "Female", "Others"]},
    contact : { type : Number, maxlength: 10},
    dob : { type: Date},
    photo_path : { type: String }
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