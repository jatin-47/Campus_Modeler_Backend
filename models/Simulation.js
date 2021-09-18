const mongoose = require('mongoose');
const ErrorResponse = require('../utils/errorResponse');

const SimulationSchema = new mongoose.Schema(
    {
		Simulation_Name: {
			type: String,
			unique: true,
			required: [true, "Input parameters cannot be empty!"],
		},
		"General Input": {
			"No of Days to Simulate": { type: Number },
			"Result Resolution by hours": { type: Number },
		},
		"Epidemic Parameter Input": {
			"Virus R0": { type: Number },
			"City Prevalence Rate": { type: Number },
			// "Expected Duration of Symptomatic Period": { type: Number },
		},
		"Policy Input": {
			// Lockdown_Capacity_of_Each_Building: { type: Number },
			// Threshold_for_AutoLockdown: { type: Number },
			"Expected No of Visitors per Day (Other than Staff)": { type: Number },
			"Compliance Rate": { type: Number },
			"Quarantine Period": { type: Number },
			"Sector/Building to Lockdown": { type: String },
			// Daily_Testing_Capacity_Increment_Rate: { type: Number },
			// Dorfman_Pool_Size: { type: Number },
			// Tapestry_Pool_Size: { type: Number },
			// Tapestry_Pool_Duplication: { type: Number },
			// Test_Sensitivity: { type: Number },
			// Test_Specificity: { type: Number },
			// Vaccine_Coverage: { type: Number },
			// Vaccine_Efficiency1: { type: Number },
			// Vaccine_Efficiency2: { type: Number },
			// Hotspot_Threshold: { type: Number },
		},
		"Testing Strategy": {
			"Testing Strategy": {
				type: String,
				enum: [
					"Complete Random",
					"Symptomatic First",
					"Symptomatic First then Hostel-wise Random",
					"Perfect Contact Tracing",
					"Risk-based Contact Tracing",
				],
				required: true,
			},
			"Testing Capacity Per Day": { type: Number },
			"Day(s) of Testing": {
				type: String,
				enum: [
					"monday",
					"tuesday",
					"wednesday",
					"thursday",
					"friday",
					"saturday",
				],
				required: true,
			},
			"Test Sensitivity": { type: Number },
			"Test Specificity": { type: Number },
		},
		user: {
			type: mongoose.Schema.Types.ObjectId,
			ref: "User",
			required: true,
		},
	},
	{ timestamps: true }
);

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