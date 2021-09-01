const mongoose = require('mongoose');

const SimulationSchema = new mongoose.Schema({
    inputJSON: {
        type: String,
        required: [true, "Input parameters cannot be empty!"]
    },
}, { timestamps: true });

const Simulation = mongoose.model("Simulation", SimulationSchema);

module.exports = Simulation;