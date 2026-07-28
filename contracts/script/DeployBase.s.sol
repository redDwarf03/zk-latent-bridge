// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "../src/LatentBridgeVerifier.sol";
import "../src/BridgeEntry.sol";

contract DeployBase is Script {
    function run() external {
        // Retrieve the deployer private key from the environment variable
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");

        // Start broadcasting transactions using the deployer's private key
        vm.startBroadcast(deployerPrivateKey);

        // 1. Deploy the EZKL-generated Verifier
        Halo2Verifier verifier = new Halo2Verifier();
        console.log("Halo2Verifier deployed at:", address(verifier));

        // 2. Deploy the BridgeEntry, passing the Verifier's address
        BridgeEntry bridge = new BridgeEntry(address(verifier));
        console.log("BridgeEntry deployed at:", address(bridge));

        // Stop broadcasting transactions
        vm.stopBroadcast();
    }
}
