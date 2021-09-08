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
    } else {
        const csvData = await csvToJson(`result/${user.username}/Hotspots.csv`);
        // console.log(csvData);
        if (csvData) {
            return response.send(csvData);
        }
    }
    return response.status(400).send({
        message: 'Bad Request',
    });
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
    } else {
        const csvData = await csvToJson(`result/${user.username}/Building_occupancy.csv`);
        // console.log(csvData);
        if (csvData) {
            return response.send(csvData);
        }
    }
    return response.status(400).send({
        message: 'Bad Request',
    });
};

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
    } else {
        const csvData = await csvToJson(`result/${user.username}/results.csv`);
        // console.log(csvData);
        if (csvData) {
            return response.send(csvData);
        }
    }
    return response.status(400).send({
        message: 'Bad Request',
    });
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
    } else {
        const csvData = await csvToJson(`result/${user.username}/locations.csv`);
        // console.log(csvData);
        if (csvData) {
            return response.send(csvData);
        }
    }
    return response.status(400).send({
        message: 'Bad Request',
    });
};
