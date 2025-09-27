require("dotenv").config();
require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */


const PRIVATE_KEY = process.env.PRIVATE_KEY || process.env.PRIVATEKEY || "";
const SEPOLIA_RPC_URL = process.env.SEPOLIA_RPC_URL || process.env.SEPOLIA_RPC || process.env.GOERLI_RPC || process.env.RPC_URL || "";
const AMOY_RPC_URL = process.env.AMOY_RPC_URL || process.env.AMOY_RPC || process.env.POLYGON_RPC || "";
const RSK_RPC_URL = process.env.RSK_RPC_URL || process.env.RSK_TESTNET_RPC || process.env.RSK_RPC || "";

module.exports = {
  solidity: "0.8.28",
  networks: {
    sepolia: {
      url: SEPOLIA_RPC_URL,
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 11155111,
    },
    amoy: {
      url: AMOY_RPC_URL,
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 80002,
    },
    rskTestnet: {
      url: RSK_RPC_URL,
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 31,
    },
  },
};
