const path = require("path");
const { getDefaultConfig } = require("expo/metro-config");

const projectRoot = __dirname;
const workspaceRoot = path.resolve(projectRoot, "../..");

const config = getDefaultConfig(projectRoot);

// Add shared folder to watch list
config.watchFolders = [workspaceRoot];

// Fix resolving packages when using symlinks
config.resolver.nodeModulesPaths = [
  path.resolve(projectRoot, "node_modules"),
  path.resolve(workspaceRoot, "node_modules"),
];

// Allow importing shared code (usually transpiled with Babel)
config.resolver.sourceExts.push("cjs");

module.exports = config;
