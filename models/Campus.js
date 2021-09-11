const mongoose = require('mongoose');

const CampusSchema = new mongoose.Schema({
    campusname: {
        type: String,
        enum: ['kharagpur','madras', 'delhi'],
        required: true
    },
    users : [{
        type : mongoose.Schema.Types.ObjectId,
        ref: 'User'
    }]
});

const Campus = mongoose.model("Campus", CampusSchema);

module.exports = Campus;