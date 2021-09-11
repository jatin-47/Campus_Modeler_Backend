const multer = require("multer");


var storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, __basedir + "/public/media/tmp");
  },
  filename: (req, file, cb) => {
    cb(null, `${Date.now()}-${file.originalname}`);
  },
});

var uploadFile = multer({ storage: storage });
module.exports = uploadFile;