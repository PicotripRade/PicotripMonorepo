// apps/mobile/metro.config.js
const path = require('path');
const extraNodeModules = {
  shared: path.resolve(__dirname, '../../shared')
};
module.exports = {
  resolver: {
    extraNodeModules
  },
  watchFolders: [path.resolve(__dirname, '../../shared')]
};
