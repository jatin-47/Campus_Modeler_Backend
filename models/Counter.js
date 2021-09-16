const mongoose = require('mongoose');
let CampusNames = require('../config/campusnames');

CampusNames.unique = true;

const CounterSchema = new mongoose.Schema({
    campusname : CampusNames,
    CampusBuilding : { type: Number},
    User : {type : Number},
    BatchStudent : {type : Number},
    Faculty : { type: Number},
    Staff : { type: Number}
});

CounterSchema.methods.increaseCount = async function (model) {
    if(model == "CampusBuilding"){
        let count = this.CampusBuilding;
        this.CampusBuilding++;
        await this.save();
        return count;
    }else if(model == "User"){
        let count = this.User;
        this.User++;
        await this.save();
        return count;
    }else if(model == "BatchStudent"){
        let count = this.BatchStudent;
        this.BatchStudent++;
        await this.save();
        return count;
    }else if(model == "Faculty"){
        let count = this.Faculty;
        this.Faculty++;
        await this.save();
        return count;
    }else if(model == "Staff"){
        let count = this.Staff;
        this.Staff++;
        await this.save();
        return count;
    }
}

const Counter = mongoose.model("Counter", CounterSchema);

module.exports = Counter;