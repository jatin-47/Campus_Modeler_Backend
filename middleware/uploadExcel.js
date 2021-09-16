const multer = require("multer");
const path = require('path');
const ErrorResponse = require('../utils/errorResponse');


const excelFilter = (req, file, cb) => {
    const filetypes = /xlsx/;
    const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = file.mimetype.includes("excel") || file.mimetype.includes("spreadsheetml");

    if (mimetype && extname) {
        cb(null, true);
    } else {
        cb(new ErrorResponse("Please upload only '.xlsx' file.",400), false);
    }
}

  
var storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, process.env.EXCEL_UPLOAD_PATH);
    },
    filename: (req, file, cb) => {
        cb(null, `${Date.now()}-${file.originalname}`);
    },
});
  
var uploadFile = multer({ 
    storage: storage, 
    limits: {fileSize : 10000000}, 
    fileFilter: excelFilter 
});
module.exports = uploadFile;