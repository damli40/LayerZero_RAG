Message Ordering
LayerZero offers both unordered delivery and ordered delivery, providing developers with the flexibility to choose the most appropriate transaction ordering mechanism based on the specific requirements of their application.

Unordered Delivery
By default, the LayerZero protocol uses unordered delivery, where transactions can be executed out of order if all transactions prior have been verified.

If transactions 1 and 2 have not been verified, then transaction 3 cannot be executed until the previous nonces have been verified.

Once nonces 1, 2, 3 have been verified:

If nonce 2 failed to execute (due to some gas or user logic related issue), nonce 3 can still proceed and execute.
Lazy Nonce Enforcement Dark

This is particularly useful in scenarios where transactions are not critically dependent on the execution of previous transactions.

Ordered Delivery
Developers can configure the OApp contract to use ordered delivery.

Strict Nonce Enforcement Dark

In this configuration, if you have a sequence of packets with nonces 1, 2, 3, and so on, each packet must be executed in that exact, sequential order:

If nonce 2 fails for any reason, it will block all subsequent transactions with higher nonces from being executed until nonce 2 is resolved.
Strict Nonce Enforcement Fail Dark

Strict nonce enforcement can be important in scenarios where the order of transactions is critical to the integrity of the system, such as any multi-step process that needs to occur in a specific sequence to maintain consistency.

info
In these cases, strict nonce enforcement can be used to provide consistency, fairness, and censorship-resistance to maintain system integrity.

Enabling Ordered Delivery
To implement strict nonce enforcement, you need to implement the following:

a mapping to track the maximum received nonce.
override _acceptNonce and nextNonce.
add ExecutorOrderedExecutionOption in _options when calling _lzSend.
a governance function to keep the nonce mapping between the protocol and application in sync when skipping nonces.
caution
If you do not pass an ExecutorOrderedExecutionOption in your _lzSend call, the Executor will attempt to execute the message despite your application-level nonce enforcement, leading to a message revert.

Append to your Message Options an ExecutorOrderedExecutionOption in your _lzSend call:

// appends "01000104", the ExecutorOrderedExecutionOption, to your options bytes array
_options = OptionsBuilder.newOptions().addExecutorLzReceiveOption(200000, 0).addExecutorOrderedExecutionOption();


Keeping Nonces In Sync
When skipping nonces at the protocol level, such as calling endpoint.skip, your OApp's local mapping must be incremented as well. If the local receivedNonce mapping falls behind the protocol's stored nonce, subsequent messages will revert with an invalid nonce error.

A governance helper could look like:

/**
 * @notice skips exactly the next‐in‐line message, and keeps our mapping in perfect sync
 * @param _srcEid the LayerZero source chain ID
 * @param _sender the address of the remote sender (packed as bytes32)
 * @param _nonce  the nonce to skip — must equal nextNonce(_srcEid,_sender)
 */
function skipInboundNonce(
  uint32 _srcEid,
  bytes32 _sender,
  uint64 _nonce
) public onlyOwner {
  // 1) sanity‐check that you're skipping exactly the next message
  uint64 expected = nextNonce();
  require(_nonce == expected, "OApp: invalid skip nonce");

  // 2) fire the skip on the endpoint
  IMessagingChannel(address(endpoint)).skip(
      address(this),
      _srcEid,
      _sender,
      _nonce
  );

  // 3) sync our mapping
  receivedNonce[_srcEid][_sender] = _nonce;
}


Keeping these values aligned ensures nextNonce returns the correct value and prevents ordered messages from being blocked.

Implement strict nonce enforcement via function override:

pragma solidity ^0.8.20;

import { OApp } from "@layerzerolabs/oapp-evm/contracts/oapp/OApp.sol"; // Import OApp and other necessary contracts/interfaces

/**
 * @title OmniChain Nonce Ordered Enforcement Example
 * @dev Implements nonce ordered enforcement for your OApp.
 */
contract MyNonceEnforcementExample is OApp {
    // Mapping to track the maximum received nonce for each source endpoint and sender
    mapping(uint32 eid => mapping(bytes32 sender => uint64 nonce)) private receivedNonce;

    /**
     * @dev Constructor to initialize the omnichain contract.
     * @param _endpoint Address of the LayerZero endpoint.
     * @param _owner Address of the contract owner.
     */
    constructor(address _endpoint, address _owner) OApp(_endpoint, _owner) {}

    /**
     * @dev Public function to get the next expected nonce for a given source endpoint and sender.
     * @param _srcEid Source endpoint ID.
     * @param _sender Sender's address in bytes32 format.
     * @return uint64 Next expected nonce.
     */
    function nextNonce(uint32 _srcEid, bytes32 _sender) public view virtual override returns (uint64) {
        return receivedNonce[_srcEid][_sender] + 1;
    }

    /**
     * @dev Internal function to accept nonce from the specified source endpoint and sender.
     * @param _srcEid Source endpoint ID.
     * @param _sender Sender's address in bytes32 format.
     * @param _nonce The nonce to be accepted.
     */
    function _acceptNonce(uint32 _srcEid, bytes32 _sender, uint64 _nonce) internal virtual override {
        receivedNonce[_srcEid][_sender] += 1;
        require(_nonce == receivedNonce[_srcEid][_sender], "OApp: invalid nonce");
    }

    // @dev Override receive function to enforce strict nonce enforcement.
    function _lzReceive(
        Origin calldata _origin,
        bytes32 _guid,
        bytes calldata _message,
        address _executor,
        bytes calldata _extraData
    ) public payable virtual override {
        _acceptNonce(_origin.srcEid, _origin.sender, _origin.nonce);
        // your _lzReceive(...) logic continues here
    }
}