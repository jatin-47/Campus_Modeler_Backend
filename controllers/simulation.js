const mongoose = require('mongoose');
const User = require('../models/User');
const Simulation = require('../models/Simulation');

const runPython = require('../utils/runPython');
const ErrorResponse = require('../utils/errorResponse');

const moment = require('moment');
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

exports.saveSimulation = async (request, response, next) => {
    const user = request.user;
    const data = request.body;
    const { simId } = request.query;
    
    try{
        if(simId){ //update
            let sim = await Simulation.findById(simId);
            if(sim.user.equals(user._id)){
                sim.GeneralInput = data.GeneralInput;
                sim.EpidemicParameterInput = data.EpidemicParameterInput;
                sim.PolicyInput = data.PolicyInput;
                sim.TestingStrategy = data.TestingStrategy;
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
                GeneralInput : data.GeneralInput,
                EpidemicParameterInput : data.EpidemicParameterInput,
                PolicyInput : data.PolicyInput,
                TestingStrategy : data.TestingStrategy,
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
    } 
    else {
        fs.rmdirSync(`result/${user.username}`, { recursive: true });
        runPython(['rakshak/run_simulation.py', JSON.stringify(request.body), `result/${user.username}`])
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
