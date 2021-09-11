const mongoose = require('mongoose');
const ErrorResponse = require('../utils/errorResponse');

const SimulationSchema = new mongoose.Schema({
    inputJSON: {
        type: String,
        required: [true, "Input parameters cannot be empty!"]
    },
    user : {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required : true
    }
}, { timestamps: true });

SimulationSchema.pre('save', async function (next) {
    try{
        const User = require('./User');
        const user = await User.findById(this.user);
        if(user){
            next();
        } 
        else{
            return next(new ErrorResponse('No such user exists',400));
        }
    }
    catch(err){
        return next(new ErrorResponse(err,400));
    }
});

const Simulation = mongoose.model("Simulation", SimulationSchema);

module.exports = Simulation;