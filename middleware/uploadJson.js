const multer = require("multer");
const path = require('path');
const ErrorResponse = require('../utils/errorResponse');


const jsonFilter = (req, file, cb) => {
    const filetypes = /json/;
    const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = file.mimetype.includes("json");
    if (mimetype && extname) {
        cb(null, true);
    } else {
        cb(new ErrorResponse("Please upload only 'json' file.",400), false);
    }
}

  
var storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, process.env.JSON_UPLOAD_PATH);
    },
    filename: (req, file, cb) => {
        cb(null, `${Date.now()}-${file.originalname}`);
    },
});
  
var uploadFile = multer({ 
    storage: storage, 
    limits: {fileSize : 10000000}, 
    fileFilter: jsonFilter 
});
module.exports = uploadFile;