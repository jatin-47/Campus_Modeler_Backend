const { spawn } = require('child_process');


const runPython = (args) => {

    // const childPython = spawn('python', ['--version']);
    const childPython = spawn('python', [...args]);

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