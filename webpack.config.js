const path = require('path')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = {
  module: {
    rules: [
      {
        test: /.css$/i,
        use: ['style-loader', 'css-loader']
      },
      {
        test: /\.vue$/,
        use: ['vue-loader']
      }
    ]
  },

  entry: path.resolve(__dirname, 'osd2f', 'javascript', 'file_upload.js'),

  output: {
    filename: 'main.js',
    library: 'file_upload',
    libraryTarget: 'window',
    path: path.resolve(__dirname, 'osd2f', 'static', 'js')
  },

  resolve: {
    alias: {
      vue$: 'vue/dist/vue.esm.js'
    },
    extensions: ['*', '.js', '.vue', '.json']
  },

  plugins: [
    new VueLoaderPlugin(),
    new CopyWebpackPlugin({
      patterns: [
        {
          // libarchive requires the distribution bundles to be available
          // for the web worker.
          from: path.resolve(
            __dirname,
            'node_modules',
            'libarchive.js',
            'dist'
          ),
          to: path.resolve(__dirname, 'osd2f', 'static', 'js', 'libarchive')
        }
      ]
    })
  ]
}
