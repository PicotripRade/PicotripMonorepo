const { getDefaultConfig } = require("expo/metro-config");
const path = require("path");

const projectRoot = __dirname;
const repoRoot = path.resolve(projectRoot, '..', '..');

const config = getDefaultConfig(__dirname);

// Add support for monorepo shared package
config.watchFolders = [
  // include monorepo root and shared package so metro watches them
  repoRoot,
  path.resolve(repoRoot, 'packages', 'shared'),
];


config.resolver = {
  ...config.resolver,
  // prefer node_modules in repo root (helps monorepo resolution)
  extraNodeModules: new Proxy({}, {
    get: (_, name) => path.join(repoRoot, 'node_modules', name),
  }),
};

module.exports = config;
