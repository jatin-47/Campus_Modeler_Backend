const mongoose = require('mongoose');
const ErrorResponse = require('../utils/errorResponse');

const SimulationSchema = new mongoose.Schema({
    Simulation_Name : {
        type: String, 
        unique : true,
        required :  [true, "Input parameters cannot be empty!"] 
    },
    GeneralInput : {
        No_of_days_to_simulate : {type: Number},
        Day_Resolution_By_Hours : {type: Number}
    },
    EpidemicParameterInput : {
        InfectionRate : {type: Number},
        RecoveryRate : {type: Number},
        Probability_of_Showing_Symptoms : {type: Number},
        Pre_SymptomaticPeriod : {type: Number}
    },
    PolicyInput : {
        Lockdown_Capacity_of_Each_Building : {type: Number},
        Threshold_for_AutoLockdown : {type: Number},
        No_of_Campus_Visitors_Allowed : {type: Number},
        Daily_Testing_Capacity : {type: Number},
        Daily_Testing_Capacity_Increment_Rate : {type: Number},
        Dorfman_Pool_Size : {type: Number},
        Tapestry_Pool_Size : {type: Number},
        Tapestry_Pool_Duplication : {type: Number},
        Test_Sensitivity : {type: Number},
        Test_Specificity : {type: Number},
        Vaccine_Coverage : {type: Number},
        Vaccine_Efficiency1 : {type: Number},
        Vaccine_Efficiency2 : {type: Number},
        Minimum_Inter_Dose_Period : {type: Number},
        Hotspot_Threshold : {type: Number},
        At_risk_Percentile_Threshold : {type: Number}
    },
    TestingStrategy : {
        type: String,
        enum: ['Random'], //to be filled
        required : true
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