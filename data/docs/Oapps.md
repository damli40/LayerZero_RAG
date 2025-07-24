Core Concepts for Omnichain Applications
LayerZero’s Omnichain Application (OApp) standard defines a generic cross-chain messaging interface that allows developers to build applications which send and receive arbitrary data across multiple blockchain networks.

Although implementations differ between Developer VMs, they share the following core concepts:

Generic Message Passing
OApp Example

Send & receive interface:
An OApp provides interface methods to send messages (by encoding data into a payload) and receive messages (by decoding that payload and executing business logic) via the LayerZero protocol. This abstraction lets you use the same messaging pattern for a variety of use cases (e.g., DeFi, DAOs, NFT transfers).

Custom logic on receipt:
Each OApp is designed so that developers can plug in their application-specific logic into the message‐handling functions. Whether you’re transferring tokens, votes, or some other data-type, the core design remains the same.

Quoting and Payment
Dynamic fee estimation:
The standard provides a mechanism to quote the required service fees for sending a cross-chain message in both the native chain token and in the protocol token, ZRO. This quote must match the gas or fee requirements at the time of sending.

Bundled fee model:
The fee paid on the source chain covers all costs: the native chain gas cost and fees for the service workers handling the transaction on the destination chain (e.g., Decentralized Verifier Networks and Executors). This unified fee model simplifies cross-chain transactions for developers and users alike.

Execution Options and Enforced Settings
Message execution options:
When sending a message, developers can specify execution options — such as the amount of gas to be used on the destination chain or other execution parameters. These options help tailor how the cross-chain message is processed once it arrives.

Enforced options:
To prevent misconfigurations or inconsistent execution, OApps can enforce a set of options (like minimum gas limits) that all senders must adhere to. This ensures that messages are processed reliably and prevents unexpected reverts or failures.

Peer and Endpoint Management
Trusted peers:
Every deployed OApp must set up trusted peers on the destination chains. This pairing (stored as a simple mapping) tells the protocol where to send messages to or expect messages from.

info
The peer’s address is stored in a format (such as bytes32) that is interoperable between VMs.

Endpoint Integration:
All cross-chain messages are sent via a standardized protocol endpoint, which handles the low-level message routing, verification management, and fee management. This endpoint acts as the bridge between disparate chains.

Administrative and Security Controls
Admin and delegate roles:
The OApp design includes built-in roles for managing and configuring the application. Typically, the contract owner (or admin) holds the authority to update peers, set execution configurations, or transfer admin rights. A separate role, the delegate, can be used to manage critical operations like security configuration updates and block finality settings.

Security measures:
Since cross-chain operations carry extra risk, developers are encouraged to use additional safeguards (e.g., governance controls, multisig wallets, or timelocks) to secure critical roles like the delegate and admin to prevent unauthorized changes.

Composition (Re-entrancy & Extended Flows)
Message composition:
Beyond simple send/receive operations, the standard can also support composing messages. This “compose” feature allows an OApp to trigger a subsequent call to itself or another contract after a message has been delivered. This is particularly useful for advanced use cases where the cross-chain message results in a series of actions rather than a single event.
VM-Specific Implementation Notes
EVM:
The OApp is implemented via Solidity contracts. Developers inherit from base contracts like OApp.sol that provide a complete messaging interface (including enforced options and fee quoting) while allowing custom logic in the _lzReceive function.

Solana:
Instead of inheritance, Solana relies on Cross Program Invocation (CPI) where the LayerZero Endpoint CPI is used. Developers build their OApp program around a set of core instructions that mirror the send/receive flow.

Aptos Move:
The Move-based OApp splits the logic into modular components (such as oapp::oapp, oapp::oapp_core, oapp::oapp_receive, and oapp::oapp_compose). Each module encapsulates parts of the messaging process—from fee quoting to message composition—while preserving the same overall flow.

