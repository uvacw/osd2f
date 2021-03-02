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
    extensions: ['*', '.js', '.vue', '.json'],
    // sql.js requires a bunch of polyfilling
    fallback: {
      crypto: require.resolve("crypto-browserify"),
      stream: require.resolve("stream-browserify"),
      buffer: require.resolve("buffer/"),
      path: require.resolve("path-browserify"),
      fs: false,
    }
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
        },
        {
          // sql.js requires sql-wasm.wasm
          from: path.resolve(
            __dirname,
            "node_modules",
            "sql.js",
            "dist",
            "sql-wasm.wasm"
          ),
          to: path.resolve(__dirname, "osd2f", "static", "js"),
        }
      ]
    })
  ]
}
