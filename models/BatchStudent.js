const mongoose = require('mongoose');
const CampusNames = require('../config/campusnames');

const BatchStudentSchema = new mongoose.Schema({
    BatchID : {type : Number},
    BatchCode : { type: String, required: true},
    Department : { type : String, enum : ['Mech','Cse','IT']},
    ProgramCode : { type: String, enum : ["BE", "ME", "PHD"]},
    YearOfStudy : {type : Number},
    Strength : { type: Number, required : true},
    Status : { type : Boolean, default: true},
    campusname : CampusNames
});

BatchStudentSchema.pre('insertMany', async function (next, docs) {
    try{
        tobeBatchCode = [];
        for(let doc of docs){            
            let isUniqueBatchCodeperCampus= await doc.isUniqueBatchCodeperCampus();
            if(!isUniqueBatchCodeperCampus) {
                throw "One or more BatchCodes are already used in the database for your campus!"
            }
            tobeBatchCode.push(doc.BatchCode.toLowerCase());
        }
        if((new Set(tobeBatchCode)).size !== tobeBatchCode.length) {
            throw "Your upload contains duplicate BatchCodes for two or more batches!"
        }
        next();
    } 
    catch (error) {
        return next(new ErrorResponse(error,400));
    }
});

BatchStudentSchema.methods.isUniqueBatchCodeperCampus = async function () {
    try {
        let batch = await BatchStudent.findOne({campusname : this.campusname, BatchCode: this.BatchCode})
        if(batch) {return false;}
        else {return true;}
    } catch(err){
        return err;
    }
}

BatchStudentSchema.methods.assignBatchID = async function () {
    const Counter = require('./Counter');

    const campusCounter = await Counter.findOne({campusname: this.campusname});
    this.BatchID = await campusCounter.increaseCount("BatchStudent"); 
    await this.save();
}

const BatchStudent = mongoose.model("BatchStudent", BatchStudentSchema);

module.exports = BatchStudent;