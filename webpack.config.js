const path = require('path');

module.exports = {
  entry: './osd2f/static/js/file_upload.js',
  output: {
    filename: 'main.js',
    library: 'file_upload',
    libraryTarget: 'window',
    path: path.resolve(__dirname, 'osd2f', 'static','js'),
  },
};