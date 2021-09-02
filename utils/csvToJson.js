const fs = require('fs');
const csvParse = require('csv-parse');


module.exports = async function csvToJson(csvPath, delimeter = ',') {
    const csvData = [];

    return new Promise((resolve, reject) => {
        const readStream = fs.createReadStream(csvPath)
        readStream.pipe(csvParse({ delimeter }))
            .on('data', function (dataRow) {
                csvData.push(dataRow);
            })
            .on('error', (error) => {
                resolve({
                    success: 'false',
                    error: error.code
                });
            })
            .on('end', function () {
                // console.log(csvData);
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
                // console.log(data);
                resolve(data);
            });
        readStream.on('error', () => resolve(null));
    });
}