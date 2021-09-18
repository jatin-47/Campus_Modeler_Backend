const CampusName = {
    type: String,
    enum: ['kharagpur','madras', 'delhi', "jodhpur", "IIT Jodhpur"],
    required: true,
    select: false
};

module.exports = CampusName;