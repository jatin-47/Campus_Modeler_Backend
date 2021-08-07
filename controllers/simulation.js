const User = require('../models/User');

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

    response.send({
        'hi': 'Hello'
    });
};

exports.savedSimulations = async (request, response, next) => {

    response.send(
        [{
            "SimulationName": 'simulation1',
            "Created_Date_Time": '10 June, 2021(12:00)'
        },
        {
            "SimulationName": 'simulation1',
            "Created_Date_Time": '10 June, 2021(12:00)'
        },
        {
            "SimulationName": 'simulation1',
            "Created_Date_Time": '10 June, 2021(12:00)'
        }]
    );
};

exports.deleteSavedSimulations = async (request, response, next) => {

    response.send({
        'message': 'Simulation Deleted'
    });
};

exports.run = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.save = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.runSavedSimulations = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};