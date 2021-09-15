const CampusName = {
    type: String,
    enum: ['kharagpur','madras', 'delhi', "jodhpur"],
    required: true,
    select: false
};

module.exports = CampusName;