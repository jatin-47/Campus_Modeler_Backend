const User = require('../models/User');
const csvParse = require('csv-parse');
const fs = require('fs');

exports.peopleCount = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};

exports.buildingOccupancy = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
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
    const csvData = [];

    fs.createReadStream('temp/init.csv').pipe(csvParse({ delimeter: ',' }))
        .on('data', function (dataRow) {
            csvData.push(dataRow);
        })
        .on('end', function () {
            let data = {};
            let header = csvData[0]
            for (let param of header) {
                data[param] = [];
            }
            for (let i = 1; i < csvData.length; i++) {
                for (let col = 0; col < header.length; col++) {
                    data[header[col]].push(csvData[i][col]);
                }
            }
            console.log(data);
            response.send(data);
        })


    console.log(csvData);
};

exports.peopleLocations = async (request, response, next) => {

    response.send({
        'hi': 'Hello'
    });
};
