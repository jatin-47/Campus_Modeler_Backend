const mongoose = require('mongoose');
const User = require('../models/User');
const CampusBuilding = require('../models/CampusBuilding');
const Simulation = require('../models/Simulation');

const runPython = require('../utils/runPython');
const ErrorResponse = require('../utils/errorResponse');

const moment = require('moment');
const fs = require('fs');

exports.policyPlanner = async (request, response, next) => {

    let buildingnames = [];

    try {
			let CampusBuildings = await CampusBuilding.find({ campusname: request.user.campusname },"BuildingName");
            CampusBuildings.forEach(element => {
                buildingnames.push(element.BuildingName)
            });
            // console.log(buildingnames);
        } catch (err) {
			return next(new ErrorResponse(err, 400));
		}
    
    response.send({
        "General Input": {
			"No of Days to Simulate": 10,
			"Result Resolution by hours": 1,
		},
		"Epidemic Parameter Input": {
			"Virus R0": 1.5,
			"City Prevalence Rate": 0.005,
            "No of Initial Infected People": 10
			// "Expected Duration of Symptomatic Period": 14,
		},
		"Policy Input": {
			// Lockdown_Capacity_of_Each_Building: { type: Number },
			// Threshold_for_AutoLockdown: { type: Number },
			"Expected No of Visitors per Day (Other than Staff)": 15,
			"Compliance Rate": 0.8,
			"Quarantine Period": 14,
			"Sector/Building to Lockdown": ["No Lockdown","Academic","Administration","Restaurant","Market","Facility","Grounds","Gymkhana","Non_Academic",...buildingnames],
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
			"Testing Strategy": ['Complete Random','Symptomatic First','Symptomatic First then Hostel-wise Random','Perfect Contact Tracing','Risk-based Contact Tracing'],
            "Testing Capacity Per Day": 30,
            "Day(s) of Testing": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
            "Test Sensitivity": 0.95,
            "Test Specificity": 1
		}
    });
};

exports.initialization = async (request, response, next) => {

    response.send({
        "Random":
        {
            "No of Initial Infected People": 10,
        },
        // "TimeSeries":
        // {
        //     "No_of_Daily_Cases": [10, 20, 30, 40],
        //     "No_of_days_to_Simulate": [10, 20, 30, 40]
        // },
        // "Spatial_Distribution": {
        //     "Spatial_Distribution": [10, 20, 30, 40]
        // }
    });
};

exports.saveSimulation = async (request, response, next) => {
    const user = request.user;
    const data = request.body;
    const { simId } = request.query;
    
    try{
        if(simId){ //update
            let sim = await Simulation.findById(simId);
            if(sim.user.equals(user._id)){
                sim["General Input"] = data["General Input"];
                sim["Epidemic Parameter Input"] = data["Epidemic Parameter Input"];
                sim["Policy Input"] = data["Policy Input"];
                sim["Testing Strategy"] = data["Testing Strategy"];
                await sim.save();

                fs.renameSync(`result/${user.username}`, `result/${user.username}_${simId}`);
                console.log("Successfully renamed the directory.")

                response.send({
                    'message': `Simulation (${sim.Simulation_Name}) updated successfully!`
                });
            }
            else{
                return next(new ErrorResponse("You are not the owner of this sim",401));
            }
        }
        else { //create_new
            //parameters saving
            const saved_sim = await Simulation.create({
                Simulation_Name : data.Simulation_Name,
                "General Input" : data["General Input"],
                "Epidemic Parameter Input" : data["Epidemic Parameter Input"],
                "Policy Input" : data["Policy Input"],
                "Testing Strategy" : data["Testing Strategy"],
                user : user._id
            });

            //results saving (basically renaming the latest temp run data folder)
            fs.renameSync(`result/${user.username}`, `result/${user.username}_${saved_sim._id}`);
            console.log("Successfully renamed the directory.")
        
            response.send({
                success: true,
                message: 'Saved Successfully'
            });
        }

    }
    catch(err) { return next(new ErrorResponse(err,400)); }
};

exports.savedSimulations = async (request, response, next) => {
    const user = request.user;
    try {
        const simulations = await Simulation.find({user: user._id});
        let desiredformat = simulations.map((curr)=> {
            new_sim = {};
            new_sim.simId = curr._id;
            new_sim.SimulationName = curr.Simulation_Name;
            new_sim.Created_Date_Time = moment(curr.createdAt).format("D MMM, YYYY (HH:mm)");
            new_sim.Updated_Date_Time = moment(curr.updateAt).format("D MMM, YYYY (HH:mm)");
            return new_sim;
        })
    
        response.send(desiredformat);
    }catch(err) { return next(new ErrorResponse(err,400)); }
};

exports.deleteSavedSimulations = async (request, response, next) => {
    const user = request.user;
    const { simId } = request.query;
    try {
        let sim = await Simulation.findById(simId);
        
        if(sim.user.equals(user._id)){
            await sim.deleteOne();
            response.send({
                'message': 'Simulation Deleted'
            });
        }
        else{
            return next(new ErrorResponse("You are not the owner of this sim",401));
        }
    }catch(err) { return next(new ErrorResponse(err,400)); }
};

exports.run = async (request, response, next) => {
    const user = request.user;
    const { simId } = request.query;

    if(simId) {
        const saved_parameters = await Simulation.findById(simId);
        fs.rmdirSync(`result/${user.username}`, { recursive: true });
        runPython(['rakshak/run_simulation.py', JSON.stringify(saved_parameters), `result/${user.username}`])

        // send saved_parameters as response
    } 
    else {
        fs.rmdirSync(`result/${user.username}`, { recursive: true });
        runPython(['rakshak/run_simulation.py', request.user.campusname, JSON.stringify(request.body), `result/${user.username}`])
    }

    console.log('\n\n\n\n\n', request.body)

    response.send({
        'hi': 'Hello1'
    });
};


// Should be removed
exports.save = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};
