const multer = require("multer");

const excelFilter = (req, file, cb) => {
    if ( file.mimetype.includes("excel") || file.mimetype.includes("spreadsheetml")) {
      cb(null, true);
    } else {
      cb("Please upload only excel file.", false);
    }
};
  
var storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, __basedir + process.env.EXCEL_UPLOAD_PATH);
    },
    filename: (req, file, cb) => {
        console.log(file.originalname);
        cb(null, `${Date.now()}-${file.originalname}`);
    },
});
  
var uploadFile = multer({ 
    storage: storage, 
    limits: {fileSize : 10000000}, 
    fileFilter: excelFilter 
});
module.exports = uploadFile;