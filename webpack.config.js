const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {
  entry: path.resolve(__dirname,"osd2f", "javascript", "file_upload.js"),
  output: {
    filename: 'main.js',
    library: 'file_upload',
    libraryTarget: 'window',
    path: path.resolve(__dirname, 'osd2f', 'static','js'),
  },

  plugins: [
    new CopyWebpackPlugin({
      patterns: [
        {
          // libarchive requires the distribution bundles to be available
          // for the web worker.          
          from: path.resolve(__dirname, "node_modules","libarchive.js","dist"), 
          to: path.resolve(__dirname, "osd2f","static","js","libarchive")
        }
      ]
    })
  ]
};