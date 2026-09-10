import { ethers } from "ethers";
import fs from "fs";

async function main() {
    // Connect to your local Hardhat node
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    
    // Use the first account from the 'npx hardhat node' list
    const signer = await provider.getSigner();

    // Load the compiled contract data (Hardhat creates this when you run compile)
    const artifactPath = "./artifacts/contracts/DPDPErasure.sol/DPDPErasure.json";
    const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));

    console.log("Deploying DPDPErasure contract...");

    // Create a Contract Factory manually
    const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, signer);

    // Deploy
    const contract = await factory.deploy();
    await contract.waitForDeployment();

    console.log("------------------------------------------");
    console.log("Contract deployed to:", await contract.getAddress());
    console.log("------------------------------------------");
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});
