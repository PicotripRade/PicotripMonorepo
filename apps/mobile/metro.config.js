const { getDefaultConfig } = require("expo/metro-config");
const path = require("path");

const config = getDefaultConfig(__dirname);

// Add support for monorepo shared package
config.watchFolders = [
  path.resolve(__dirname, "../../packages/shared"),
];

config.resolver = {
  ...config.resolver,
  extraNodeModules: {
    "@picotrip/shared": path.resolve(__dirname, "../../packages/shared"),
  },
};

module.exports = config;
