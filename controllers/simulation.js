const mongoose = require('mongoose');
const User = require('../models/User');
const Simulation = require('../models/Simulation');
const runPython = require('../utils/runPython');

const ErrorResponse = require('../utils/errorResponse');

const fs = require('fs');

exports.policyPlanner = async (request, response, next) => {

    response.send({
        "GeneralInput":
        {
            "No_of_days_to_simulate": [1, 2, 3, 4],
            "Day_Resolution_By_Hours": [3, 6, 5, 4]
        },
        "EpidemicParameterInput":
        {
            "InfectionRate": 0.5,
            "RecoveryRate": [0.25, 0.5, 0.75, 1],
            "Probability_of_Showing_Symptoms": [0.25, 0.5, 0.75, 1],
            "Pre_SymptomaticPeriod": [1, 2, 3, 4]
        },
        "PolicyInput":
        {
            "Lockdown_Capacity_of_Each_Building": [0.25, 0.5, 0.75, 1],
            "Threshold_for_AutoLockdown": [1, 2, 3, 4],
            "No_of_Campus_Visitors_Allowed": [50, 60, 70, 80],
            "Daily_Testing_Capacity": [25, 50, 75, 100],
            "Daily_Testing_Capacity_Increment Rate": [1, 2, 3],
            "Dorfman_Pool_Size": [25, 50, 75, 100],
            "Tapestry_Pool_Size": [50, 60, 70, 80],
            "Tapestry_Pool_Duplication": [1, 2, 3, 4, 5],
            "Test_Sensitivity": [50, 60, 70, 80],
            "Test_Specificity": [50, 60, 70, 80],
            "Vaccine_Coverage": [50, 60, 70, 80],
            "Vaccine_Efficiency1": [50, 60, 70, 80],
            "Vaccine_Efficiency2": [50, 60, 70, 80],
            "Minimum_Inter-Dose_Period": [50, 60, 70, 80],
            "Hotspot_Threshold": [50, 60, 70, 80],
            "At-risk_Percentile_Threshold": [50, 60, 70, 80],
        },
        "TestingStrategy": {
            "TestingStrategy": ["Random"]
        }
    });
};

exports.initialization = async (request, response, next) => {

    response.send({
        "Random":
        {
            "No_of_People_Affected": [10, 20, 30, 40],
            "Day_Resolution_by_Hours": [1, 4, 6, 7]
        },
        "TimeSeries":
        {
            "No_of_Daily_Cases": [10, 20, 30, 40],
            "No_of_days_to_Simulate": [10, 20, 30, 40]
        },
        "Spatial_Distribution": {
            "Spatial_Distribution": [10, 20, 30, 40]
        }
    });
};

// Create a new sim if there is no simId provided.
// Update the existing sim if there's a simId provided and sim exists with that ID in the user
exports.saveSimulation = async (request, response, next) => {
    const user = request.user;
    try{
        const newSim = await Simulation.create({
            inputJSON: JSON.stringify(request.body),
            user : user._id
        });

        response.send({
            success: true,
            message: 'Simulation added to user simulations'
        });

    }catch(err) { return next(new ErrorResponse(err,400)); }
};

exports.savedSimulations = async (request, response, next) => {
    const user = request.user;
    try {
        const simulations = await Simulation.find({user: user._id});
        let desiredformat = simulations.map((curr)=> {
            new_sim = {};
            new_sim.simId = curr._id;
            new_sim.SimulationName = JSON.parse(curr.inputJSON).Simulation_Name;
            new_sim.Created_Date_Time = curr.createdAt;
            return new_sim
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
            sim.deleteOne();
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

    if (simId) {
        // update it
    } else {
        await fs.rmdirSync(`result/${user.username}`, { recursive: true });
        runPython(['rakshak/run_simulation.py', JSON.stringify(request.body), `result/${user.username}`])
    }
    /*
    const newSim = await Simulation.create({
        inputJSON: JSON.stringify(request.body)
    });
    */

    console.log('\n\n\n\n\n', request.body)

    // user.simulations.push(newSim);
    // user.save();

    // console.log(request.body);
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
