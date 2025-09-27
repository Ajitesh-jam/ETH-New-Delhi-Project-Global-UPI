const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();

  console.log("Deploying contracts with account:", deployer.address);

  const balanceBigNumber = await hre.ethers.provider.getBalance(deployer.address);
  
  const balance = await hre.ethers.formatEther(balanceBigNumber);

  console.log("Account balance:", balance, "ETH");

  await hre.run("compile");

  const PaymentSender = await hre.ethers.getContractFactory("PaymentSender");
  const paymentSender = await PaymentSender.deploy();
  await paymentSender.waitForDeployment();

  const deployedAddress = await paymentSender.getAddress();

  console.log(" PaymentSender deployed to:", deployedAddress);
}


main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
