const { spawn } = require('child_process');


const runPython = (args) => {

    // const childPython = spawn('python', ['--version']);

    // const childPython = spawn('python', [...args]);rakshak/env/bin/python
    const childPython = spawn('rakshak/env/bin/python', [...args]);

    childPython.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    childPython.stderr.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    childPython.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });

}

module.exports = runPython;