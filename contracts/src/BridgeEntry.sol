// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IVerifier {
    function verifyProof(bytes calldata proof, uint256[] calldata instances) external returns (bool);
}

contract BridgeEntry {
    IVerifier public verifier;

    event BridgeProcessed(uint256[] instances);

    constructor(address _verifier) {
        verifier = IVerifier(_verifier);
    }

    function processBridge(bytes calldata proof, uint256[] calldata instances) public {
        require(verifier.verifyProof(proof, instances), "Invalid ZK proof");
        // State processing after valid ZK proof
        emit BridgeProcessed(instances);
    }
}
