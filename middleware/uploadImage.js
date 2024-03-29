const multer = require("multer");
const path = require('path');

const imageFilter = (req, file, cb) => {
    const filetypes = /jpeg|jpg|png/;
    const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = filetypes.test(file.mimetype);
    if (mimetype && extname) {
        return cb(null, true);
    } else {
        cb("Please upload only image(.jpeg/.jpg/.png) file.", false);
    }
};

var storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, process.env.IMG_UPLOAD_PATH);
    },
    filename: (req, file, cb) => {
        cb(null, `${Date.now()}-${file.originalname}`);
    },
});

var uploadFile = multer({ 
    storage: storage, 
    limits: {fileSize : 10000000}, 
    fileFilter: imageFilter 
});
module.exports = uploadFile;