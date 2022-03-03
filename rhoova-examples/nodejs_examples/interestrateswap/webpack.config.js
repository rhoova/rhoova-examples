//

const path = require('path');
const webpack = require('webpack')
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {
    entry: {
        main: path.resolve(__dirname, './src/index.js'),
    },
    output: {
        path: path.resolve(__dirname, './dist'),
        filename: '[name].bundle.js',
    },
    watch: true,
    plugins: [
        new HtmlWebpackPlugin({
            title: 'Rhoova Example',
            template: path.resolve(__dirname, './src/template.html'),
        }),
        new CleanWebpackPlugin(),
        new webpack.HotModuleReplacementPlugin()
    ],
    module: {
        rules: [{
            test: /\.css$/i,
            use: ["style-loader", "css-loader"],
        },
        //     {
        //     test: /\.js$/,
        //     exclude: /(node_modules)/,
        //     use: {
        //         loader: 'babel-loader',
        //         options: {
        //             presets: ['babel-preset-env']
        //         }
        //     }
        // }
        ]
    },
    mode: 'development',
    devServer: {
        historyApiFallback: true,
        static: path.resolve(__dirname, './dist'),
        open: true,
        compress: true,
        hot: true,
        port: 8080,
    }
};