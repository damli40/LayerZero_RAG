What is LayerZero/lz

LayerZero is an omnichain messaging protocol — a permissionless, open framework designed to securely move information between blockchains. It empowers any application to bring its own security, execution, and cross-chain interaction, providing a predictable and adaptable foundation for decentralized applications living on multiple networks.

Before LayerZero, cross-chain communication was a patchwork of monolithic bridges and isolated solutions. Achieving true cross-chain communication was a complex and often fragile endeavor.

Traditional methods relied on monolithic bridges with centralized verifiers or a fixed set of signers — approaches that imposed rigid structures and created single points of failure. When any component of these systems faltered, every connected application was put at risk, stifling innovation and leaving developers scrambling for secure solutions.

The LayerZero Framework
LayerZero redefines cross-chain interactions by combining several key architectural elements:

Immutable Smart Contracts:
Non-upgradeable endpoint contracts are deployed on each blockchain. These immutable contracts serve as secure entry and exit points for messages, ensuring consistency and trust across all networks.

Configurable Message Libraries:
LayerZero offers flexible libraries that developers can select to tailor the way messages are emitted off-chain. This adaptability means applications can optimize message formatting and handling according to specific needs without being tied to a one-size-fits-all solution.

Modular Security Owned by the Application:
Instead of relying on a centralized verifier network, LayerZero enables each application to configure its own security stack. Developers can choose from various decentralized verifier networks (DVNs) and set parameters like finality and execution rules. This modular approach shifts control to the application, allowing for tailored security that evolves with emerging technologies.

Permissionless Execution:
By making the execution of cross-chain messages available to anyone, LayerZero ensures that once a message is verified, it can be executed without gatekeepers. This open design removes bottlenecks and facilitates seamless interaction across the blockchain mesh.

Together, these elements create a robust foundation that makes the following primitives possible.

Key Primitives Built into LayerZero
LayerZero’s architecture provides a robust set of core primitives that redefine cross-chain interaction. Each primitive has its own dedicated deep-dive section in our documentation to help you fully leverage its capabilities:

Omnichain Message Passing (Generic Messaging):
This primitive enables applications to send and receive arbitrary data across a fully-connected mesh of blockchains. Applications can push state transitions to any network in the LayerZero mesh.

Learn more in our Omnichain Applications (OApp) overview.

Omnichain Tokens (OFT & ONFT): Unified token standards that empower the cross-chain transfer of both fungible and non-fungible tokens. These standards ensure a consistent global supply through mechanisms like burn/mint or lock/unlock—abstracting away the differences across blockchain environments and providing a seamless token experience.

For additional details, refer to our Omnichain Tokens (OFT & ONFT) section.

Omnichain State Queries (lzRead):
Go beyond simple messaging—this primitive allows smart contracts to request and retrieve on-chain state from other blockchains securely. It empowers your applications to “pull” data across chains efficiently.

Dive deeper into this capability in our Omnichain Queries (lzRead) section.

Omnichain Composability:
By decoupling security from execution, this design enables developers to build complex, multi-step workflows across chains. It breaks down cross-chain operations into discrete, manageable messages that achieve instant finality, facilitating advanced use cases and improved user experiences.

For detailed insights, refer to our Omnichain Composability documentation.

These primitives provide the building blocks for predictable, secure, and scalable cross-chain interactions within the LayerZero mesh network.

Further Reading
To dive deeper into LayerZero and its omnichain capabilities, explore our detailed documentation across three core sections:

Protocol Overview: Understand the technical architecture behind LayerZero—from immutable smart contracts and configurable message libraries to the secure transmission of cross-chain messages.

Workers Overview: Learn about the off-chain service providers—Decentralized Verifier Networks (DVNs) and Executors—that play a critical role in verifying and executing cross-chain messages.

Omnichain Applications (OApp) Standard: Discover how to build applications that leverage LayerZero’s omnichain messaging interface, allowing for generic message passing, dynamic fee estimation, and secure, composable cross-chain interactions.

These sections offer comprehensive guides, best practices, and technical references to help you build secure, scalable, and truly omnichain solutions.

Protocol Overview
To send a cross-chain message, a user must write a transaction on both the source and destination blockchains.

At its core, the LayerZero protocol defines a channel between a sender and a receiver smart contract by leveraging two key components:

Source and Destination Endpoints:
Each supported blockchain deploys an immutable, permissionless Endpoint contract. On the source chain, a smart contract calls the Endpoint’s entry function (endpoint.send()) to send a message. On the destination chain, a smart contract authorizes the Endpoint to act as an exit point to receive and process that same message (endpoint.lzReceive()).

Channel Definition:
A unique messaging channel in LayerZero is defined by four specific components:

Sender Contract (Source OApp): The contract initiating the cross-chain communication.

Source Endpoint ID: The identifier for the Endpoint on the source chain.

Destination Endpoint ID: The identifier for the Endpoint on the destination chain.

Receiver Contract (Destination OApp): The contract designated to receive and process the message on the destination chain.

Within each channel, message ordering is maintained through nonce tracking. This ensures that messages are delivered exactly once.

For example, if a token bridge on one chain sends a message to its counterpart on another chain, the messages flow through a dedicated channel — distinct from all other application pathways between those chains — preserving the integrity and sequence of communication.

How the Protocol Works
Protocol V2 Dark

Message Dispatch on the Source Chain:
A smart contract on the source blockchain initiates the process by calling the Endpoint's entry function. This call includes an arbitrary message payload, details of the destination Endpoint, and the receiver's contract address. The Endpoint then uses a configurable Message Library to generate a standardized Message Packet based on the sender contract’s configuration.

Establishing a Secure Channel:
The generated Message Packet is emitted as an event by the source Endpoint. This packet contains critical information—including source and destination Endpoint IDs, the sender's and receiver’s addresses, and the message payload—which collectively define a unique messaging channel.

Verification and Nonce Management:
On the destination chain, the configured Security Stack (Decentralized Verifier Networks) deliver the corresponding payload hash to the receiver contract's configured Message Library. Once the threshold of DVN verifications satisfies the X of Y of N configuration, the Message Packet can be marked as verified and committed to the destination channel, ensuring exactly-once delivery.

Message Execution on the Destination Chain:
Finally, a caller (typically an authorized smart contract like the Executor) calls the Endpoint’s exit function lzReceive to trigger the execution of the verified message. This call delivers the message payload to the receiver contract, which can then execute its defined logic based on the incoming data.

Security and Flexibility
Immutable and Permissionless Design:
The core Endpoint contracts are immutable and permissionless. This ensures that the protocol remains secure and resistant to unauthorized changes, regardless of which virtual machine (VM) or blockchain environment is used.

VM-Agnostic Integration:
The LayerZero protocol itself is designed to be VM agnostic. The same fundamental principles apply whether you’re working with Solidity on Ethereum, Rust on Solana, Move on Aptos, or any other supported environment.

Independent Channel Management:
Each channel between a given pair of endpoints maintains its own independent message sequence. This means that multiple applications can communicate across the same chain pairs without interference, providing scalability and flexibility in designing cross-chain solutions.

Omnichain Mesh Network
LayerZero’s Omnichain Mesh is the idea that every application’s smart contract—deployed on its respective blockchain—forms part of a single, fully interconnected system. Rather than limiting an application to communicating only with a select group of chains, the protocol enables any deployed LayerZero Endpoint (the contract interface on each chain) to interact directly with any other Endpoint across all supported blockchains.

What Is the LayerZero Mesh?

Omnichain Dark

Points on the Mesh:
Every blockchain LayerZero supports has one canonical LayerZero Endpoint deployed per protocol version. This means that on each chain, there is a single, unique smart contract, the LayerZero Endpoint, that provides a consistent interface for sending and receiving messages for all applications. As a result, each Endpoint acts as a distinct “point” in the mesh, ensuring that all cross-chain communication adheres to the same standards and is easily identifiable.

Pathways on the Mesh:
When two smart contracts on different chains communicate, they create a pathway between their respective Endpoints. Think of a pathway as a direct communication channel between one Endpoint (point A) and another (point B).

A Fully Connected Network:
The mesh is “omnichain” because it allows every Endpoint to set up a communication pathway with any other Endpoint using a common interface. In other words, an application is not limited to interacting with only a subset of chains. Any Endpoint can reach out and communicate with any other Endpoint using consistent data structures and handling, ensuring seamless interoperability across the entire network.

Omnichain Features
Universal Network Semantics:
The network enforces uniform standards for message delivery regardless of the blockchain pair involved. This guarantees that data packets are reliably transferred and delivered exactly once, while preserving censorship resistance.

Modular Security Model:
LayerZero enables configurable security tailored per application for each pathway:

Decentralized Verifier Networks (DVNs) validate messages according to application–specific requirements.
Configurable Block Confirmations protect against chain reorganizations by waiting a specified number of blocks before verification.
The Endpoint’s immutable core ensures that essential security features—like protection against censorship, replay attacks, and unauthorized code changes—are consistently maintained across the entire network.
Channel Security:
Each communication channel, defined by the source blockchain, source application, destination blockchain, and destination application, can be individually configured to match the security and cost–efficiency requirements of that particular connection between endpoint and applications.

Chain Agnostic Applications:
With these universal standards in place, developers can build Omnichain Applications (OApps) that seamlessly operate across all supported blockchains, making it easy to transfer data and value across different networks.

In summary, the Omnichain Mesh Network in LayerZero is a fully connected system where every Endpoint on every supported blockchain can directly interact with any other. This design empowers developers to create applications with truly universal cross-chain capabilities—ensuring seamless, secure, and reliable messaging regardless of the underlying blockchain.

Omnichain Mesh Network
LayerZero’s Omnichain Mesh is the idea that every application’s smart contract—deployed on its respective blockchain—forms part of a single, fully interconnected system. Rather than limiting an application to communicating only with a select group of chains, the protocol enables any deployed LayerZero Endpoint (the contract interface on each chain) to interact directly with any other Endpoint across all supported blockchains.

What Is the LayerZero Mesh?

Omnichain Dark

Points on the Mesh:
Every blockchain LayerZero supports has one canonical LayerZero Endpoint deployed per protocol version. This means that on each chain, there is a single, unique smart contract, the LayerZero Endpoint, that provides a consistent interface for sending and receiving messages for all applications. As a result, each Endpoint acts as a distinct “point” in the mesh, ensuring that all cross-chain communication adheres to the same standards and is easily identifiable.

Pathways on the Mesh:
When two smart contracts on different chains communicate, they create a pathway between their respective Endpoints. Think of a pathway as a direct communication channel between one Endpoint (point A) and another (point B).

A Fully Connected Network:
The mesh is “omnichain” because it allows every Endpoint to set up a communication pathway with any other Endpoint using a common interface. In other words, an application is not limited to interacting with only a subset of chains. Any Endpoint can reach out and communicate with any other Endpoint using consistent data structures and handling, ensuring seamless interoperability across the entire network.

Omnichain Features
Universal Network Semantics:
The network enforces uniform standards for message delivery regardless of the blockchain pair involved. This guarantees that data packets are reliably transferred and delivered exactly once, while preserving censorship resistance.

Modular Security Model:
LayerZero enables configurable security tailored per application for each pathway:

Decentralized Verifier Networks (DVNs) validate messages according to application–specific requirements.
Configurable Block Confirmations protect against chain reorganizations by waiting a specified number of blocks before verification.
The Endpoint’s immutable core ensures that essential security features—like protection against censorship, replay attacks, and unauthorized code changes—are consistently maintained across the entire network.
Channel Security:
Each communication channel, defined by the source blockchain, source application, destination blockchain, and destination application, can be individually configured to match the security and cost–efficiency requirements of that particular connection between endpoint and applications.

Chain Agnostic Applications:
With these universal standards in place, developers can build Omnichain Applications (OApps) that seamlessly operate across all supported blockchains, making it easy to transfer data and value across different networks.

In summary, the Omnichain Mesh Network in LayerZero is a fully connected system where every Endpoint on every supported blockchain can directly interact with any other. This design empowers developers to create applications with truly universal cross-chain capabilities—ensuring seamless, secure, and reliable messaging regardless of the underlying blockchain.

Message Channel Security
Cross‑chain messaging introduces unique security challenges: the total value moved between chains often far exceeds what any single validator set can effectively protect. LayerZero's architecture isolates risk per pathway, ensuring security measures can scale directly with the value in the channel.

Why Traditional Bridges Struggle
Most cross‑chain bridges rely on a single, global validator set to secure all transfers between networks. This creates a concentration of risk: any attack compromises the entire pool of bridged assets rather than a specific transfer.

Asset Value Secured	Security Scope	Security Implication
All cross‑chain value	Single validator set	Large aggregated target for attackers
Because their security isn't partitioned per application pathway, traditional bridges expose every asset moving across chains to the same risk; making them a high‑value target for adversaries.

LayerZero's Channel Security Model
LayerZero avoids this misalignment by decoupling security from aggregate network value. Instead of one monolithic bridge, it partitions trust into per‑channel security configurations. Each unique pathway (sender → source Endpoint → destination Endpoint → receiver) is secured by its own configuration of Decentralized Verifier Networks (DVNs).

Configurable Channel‑Level Security (X‑of‑Y‑of‑N)
Every application defines its own security parameters:

Parameter	Definition	Effect on Security & Cost
X	Specific DVNs required to always witness a message	Higher X increases fault tolerance by controlling which DVNs must always agree
Y	Total DVN threshold (required + optional)	Ensures specific DVNs always verify while the remainder come from any members of the broader pool, balancing specificity and decentralization
N	Total DVNs available	Maximum pool of DVNs for the channel
Key Benefits
Granular Risk Isolation: Attackers can only target a specific channel's value, not the entire cross‑chain mesh.

Economic Alignment: Security scales with the channel's value, so higher‑value paths can require stronger DVN configurations.

Configurable Trade‑Offs: High‑value channels can opt for larger X/Y/N thresholds; low‑value channels can reduce them to minimize cost and latency.

Why LayerZero's Approach Is More Secure
Feature	LayerZero Channel Security	Monolithic Bridges
Economic Attack Cost	Scoped to individual channel value	Covers every connected chain's value
Attack Surface	Isolated per channel	Entire network mesh
Security Cost Alignment	Matches collateral to channel value	Single validator set must cover all value
Configurability	Adjustable per channel	Fixed, global configuration
Immutability	Only adjustable by application	Core interfaces upgradeable via multisig
While no system can guarantee per‑pathway collateral that always exceeds transferred value, LayerZero's design dramatically raises the economic cost of a successful attack compared to existing bridges.

Impact
LayerZero is today the only modular cross‑chain messaging framework that is both fully permissionless and immutable.

Once an application defines its channel's X‑of‑Y‑of‑N security settings, those parameters are enforced at the protocol level indefinitely. Only the application delegate can update these configurations. There is no governance, upgrade mechanism, or external actor that can alter or disable a channel's configuration once set, guaranteeing that security guarantees persist without relying on LayerZero.

By partitioning security and allowing each channel to calibrate its own verifier quorum, LayerZero achieves a practical balance between robust protection and efficient operation, delivering a more economically sound, scalable omnichain architecture.

Message Options
In the LayerZero protocol, message options are a way for applications to describe how they want their messages to be handled by off-chain infrastructure. These options are passed along with every message sent through LayerZero and are formatted as serialized bytes; a universal language that both the protocol and workers (like DVNs and Executors) can understand.

Each option acts like an instruction or a setting for a specific worker. For example, you might request that a certain amount of gas / compute units are allocated to execute your message on the destination chain, or that some native tokens be delivered along with the message.

Options are how applications communicate verification and execution preferences to the off-chain workers that carry out cross-chain messages.

How Does LayerZero Route Options?
When an application sends a message through LayerZero, it includes a field called options. This field is a compact, structured byte array that can contain multiple worker-specific instructions. LayerZero doesn’t interpret these options directly; instead, it forwards them to the appropriate service providers (called workers) that know how to read and act on the instructions.

The workers typically fall into two categories:

Decentralized Verifier Networks (DVNs): These provide verification to ensure the message is valid and has not been tampered with.

Executors: These are responsible for delivering and executing the message on the destination chain.

The LayerZero messaging library understands how to break apart the options and route them to the correct workers. Since applications can configure message libraries, this design is modular, as new types of workers and options can be added over time without changing the core protocol.

Enforcing Options
Some applications may require strict guarantees on how their messages are handled. Without this enforcement, users could accidentally (or maliciously) send messages that fail to execute, leading to a poor user experience or even stuck tokens.

To prevent this, applications can enforce options. Enforcement means the application itself verifies and guarantees that a specific set of options is always present and correctly formatted before the message is allowed to be sent.

Enforced options helps by:

Preventing underfunded executions that would otherwise fail on the destination chain.

Protecting users who omit critical options for a specific application use case.

Providing a consistent baseline experience regardless of the sender’s intent.

This concept is especially important in applications like token bridges, composable smart contracts, or stateful protocols where execution must be predictable and reliable.

info
Enforcing options means your application checks that users provide the correct options when calling the Endpoint's send() method. However, this does NOT guarantee that the specified instructions (e.g., gas limits or native drops) will be executed as intended by the worker or respected by permissionless callers on the destination chain.

If your application requires strict guarantees, such as an exact gas amount or mandatory native gas drops, you must also validate those conditions on-chain at the destination, or use a worker you trust. See the Integration Checklist for guidance on how to enforce execution requirements inside your _lzReceive() or lzCompose() logic.

Extra Options
While enforced options protect the base behavior of an application, users often have additional use cases that require more flexibility.

To support this, LayerZero applications can also allow users to supply extra options. These are user-defined additions to the enforced baseline, offering more granular control over the message’s behavior on the destination chain.

Why would a user want to add extra options?
Take the example of an Omnichain Token (OFT) that supports Omnichain Composability; allowing the token to trigger additional logic after being received. This logic might involve calling another contract, performing swaps, or interacting with a dApp on the destination chain.

In this case, the user might want to pay for:

A required amount of gas to ensure lzReceive() succeeds (enforced by the app).

Extra gas to support additional post-processing via lzCompose() (added by the user).

By adding these extra options, users pay to extend the functionality without modifying the underlying application logic.

Another example: Token + Native Gas Drop
Suppose a user is bridging USDT0 (an OFT) to a new chain and wants to start interacting with dApps right away. Normally, they'd receive the token, but they wouldn’t have any native gas on the destination chain to pay for further transactions.

With extra options, the user can:

Ensure lzReceive() executes successfully to receive the USDT0.

Add a native token drop option, funding their wallet with native gas on arrival.

From the user's perspective, they complete a single cross-chain action and arrive on the new chain with both:

The token they sent (USDT0)

Enough native gas to immediately start interacting

This separation of concerns makes the system both secure by default and flexible by design; a core benefit of LayerZero's modular architecture.

Why Do Options Matter?
When sending a cross-chain message, the source chain has no direct knowledge of the destination chain’s state: things like how much gas is needed, what the native currency is, or how the contract should be called.

Options solve this by letting the sender provide detailed instructions about how the message should be processed once it arrives.

Some common examples include:

Execution Gas: Telling the Executor how much gas or native token the destination contract will need during lzReceive().

Composer Gas: Adding gas or native tokens for the composer contract when calling calling lzCompose().

Native Token Drops: Sending native tokens (like ETH or APT) separately from the message.

These instructions are interpreted by the off-chain workers, so that the message is handled as expected.

Key Takeaways
options are serialized instructions that help off-chain workers understand how to process a message.

Each type of worker (DVN, Executor, etc.) looks for specific options relevant to their task.

Applications can enforce options to require correct behavior on source.

Users can extend options for extra functionality on destination.

The LayerZero protocol’s modular design means it can support new worker types without breaking existing behavior.