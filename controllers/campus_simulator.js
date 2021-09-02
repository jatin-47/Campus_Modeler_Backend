const User = require('../models/User');
const csvToJson = require('../utils/csvToJson');
const Simulation = require('../models/Simulation');
const ErrorResponse = require('../utils/errorResponse');

exports.peopleCount = async (request, response, next) => {
    const user = request.user;
    const { simId } = request.query;

    if (simId) {
        const csvData = await csvToJson(`result/${user.username}_${simId}/Hotspots.csv`);
        // console.log(csvData);
        if (csvData) {
            return response.send(csvData);
        } else {
            return next(new ErrorResponse('People count of this simulation not found', 404));
        }
    }
    return next(new ErrorResponse('Bad Request', 400));
};

exports.buildingOccupancy = async (request, response, next) => {
    const user = request.user;
    const { simId } = request.query;

    if (simId) {
        const csvData = await csvToJson(`result/${user.username}_${simId}/Building_occupancy.csv`);
        // console.log(csvData);
        if (csvData) {
            return response.send(csvData);
        } else {
            return next(new ErrorResponse('Building Occupancy of this simulation not found', 404));
        }
    }
    return next(new ErrorResponse('Bad Request', 400));
};

// Access csv file and returning data
/* 

{
    "Cumulative_infections": [47],
    "Active_infections": [31],
    "Daily_infections": [7],
    "Cumulative_positive_cases": [31],
    "Active_cases": [18],
    "Daily_positive_cases": [4],
    "Cumulative_symptomatic": [31],
    "Recovered": [9],
    "Died": [4]
}

*/
exports.caseStatistics = async (request, response, next) => {
    const user = request.user;
    const { simId } = request.query;

    if (simId) {
        const csvData = await csvToJson(`result/${user.username}_${simId}/results.csv`);
        // console.log(csvData);
        if (csvData) {
            return response.send(csvData);
        } else {
            return next(new ErrorResponse('Case statistics of this simulation not found', 404));
        }
    }
    return next(new ErrorResponse('Bad Request', 400));
};

exports.peopleLocations = async (request, response, next) => {
    const user = request.user;
    const { simId } = request.query;

    if (simId) {
        const csvData = await csvToJson(`result/${user.username}_${simId}/locations.csv`);
        // console.log(csvData);
        if (csvData) {
            return response.send(csvData);
        } else {
            return next(new ErrorResponse('People locations of this simulation not found', 404));
        }
    }
    return next(new ErrorResponse('Bad Request', 400));
};
