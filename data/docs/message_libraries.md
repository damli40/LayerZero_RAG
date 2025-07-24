Message Library Overview
The Message Library is a fundamental concept in the LayerZero protocol that encompasses how the protocol can both send and receive messages. These libraries are responsible for processing, encoding / decoding, and verifying messages as they traverse between blockchains.

Why Do Message Libraries Exist?
While specific implementations may vary to accommodate different use cases (e.g., push-based messaging versus pull-based queries), several common themes form the backbone of all Message Libraries.

Modularity & Separation of Concerns
Message Libraries are designed to abstract and isolate the core functions of cross-chain messaging. By separating tasks (e.g., encoding / decoding packets, fee calculation and management, configuration enforcement) from higher-level application logic and the LayerZero Endpoint, each library can be independently developed, optimized, and updated. This modularity enables:

Independent Optimization: Specialized libraries (like the Ultra Light Node) can be created without affecting how other parts of the protocol operate.

Easier Maintenance: The well-defined boundaries between components result in a cleaner, more maintainable architecture.

Immutable and Append-Only Design
Once deployed, Message Libraries are immutable and act as append-only components. This means that:

Predictability: The behavior of a library remains consistent over time, ensuring that applications can rely on its functionality.

Backward Compatibility: New libraries can be added to the ecosystem without affecting existing applications. This allows the protocol to evolve; integrating innovations and optimizations, while preserving the performance and security of the deployed components.

Customizability and Flexibility
Each Message Library supports a range of configurations, which applications set via the LayerZero Endpoint. These configurations determine critical aspects of message processing:

Send Libraries: Custom configurations define how packets are encoded and how fees are computed for routing messages outbound from a source chain.

Receive Libraries: Configurations specify the required verification parameters that must be met before a message is accepted and routed inbound to the destination receiver.

This flexibility allows the system to support various messaging paradigms, such as push-based messaging (e.g., Ultra Light Node) or pull-based queries (e.g., Read Library).

Security and Integrity
Security is embedded at every layer of the message lifecycle:

Encoding Integrity: On the send side, messages are wrapped in a standardized Packet that includes unique identifiers, nonces, and routing metadata to prevent replay attacks and misrouting.

Rigorous Verification: On the receive side, libraries perform stringent checks to ensure the message has not been tampered with.

Configuration Enforcement: Receive libraries enforce that only the preconfigured, authorized workers can validate and process the incoming message, adding an extra layer of security.

Efficiency and Decoupling
Efficiency is achieved by:

Streamlined Processing: Specialized libraries focus on only transmitting and processing the essential data needed for a specific messaging workflow, reducing overhead.

Decoupled Logic: By decoupling message processing from the Endpoint and application code, the protocol supports rapid processing and efficient scaling without compromising on security or flexibility.

Benefits for Developers and Users
Reliability: Immutable, well-defined libraries ensure that cross-chain messaging remains consistent and dependable.

Security: Robust verification and configuration enforcement guard against unauthorized access or tampering.

Flexibility: Developers can choose from different library implementations that best match their application's needs, with the assurance that new capabilities will be seamlessly added.

Scalability: The append-only nature of these libraries enables the protocol to integrate new innovations without disrupting existing deployments.

In summary, the Message Library is a key building block in the LayerZero protocol that unifies the processes of message encoding, transmission, decoding, and verification. Its modular, immutable, and flexible design ensures that the protocol can adapt over time while delivering secure, efficient, and reliable cross-chain communication.

Further Reading
For details on how messages are processed on the sending side, see the Message Send Library page.

For details on how inbound messages are decoded and verified on the receiving side, see the Message Receive Library page.

Message Send Library
The Message Send Library is a core component of the LayerZero protocol that manages the internal mechanics of sending messages between blockchain networks. It functions as a dedicated message handler and routing contract that connects high-level application logic with the low-level workers responsible for cross-chain communication.

What Is a Message Send Library?
The Message Send Library is responsible for several key tasks that enable reliable message delivery:

Encoding Packets: It packages outgoing message packets from the LayerZero Endpoint by encoding the unique identifiers, nonces (which help maintain the correct order), and other metadata. This process ensures that each message is uniquely identifiable and traceable across networks.

Calculating Fees: While processing a packet, the library computes and returns fee details back to the endpoint based on the worker settings defined by the application. This ensures that all cost-related aspects of message delivery are handled accurately.

Managing Configuration: Applications set configuration parameters via the LayerZero Endpoint, which are then applied to the library’s internal worker logic. This means that the library processes messages based on custom application settings for routing and fee management.

The Message Send Library acts as a specialized routing contract to direct how packets are encoded, how fees are computed, and how configurations shape the overall message delivery process.

How It Fits Into the Protocol
LayerZero’s design splits the cross-chain messaging process into clear, sequential steps:

Send Model Flow:
Application → Endpoint → Message Send Library → Workers

Application: The sender smart contract initiates a message for a fee.

Endpoint: Acting as the entrypoint, the endpoint moves the message inside a packet, and leverages the application’s settings to determine which Message Send Library to invoke.

Message Send Library: The library processes the packet by encoding it, calculating fees for the given configuration settings, and routing the encodedPacket to the appropriate workers.

Workers: These service providers handle the actual transmission and execution of the encodedPacket, ensuring it reaches its intended destination.

Send Ultra Light Node (ULN)
A specialized version of the Message Library is the Ultra Light Node (ULN). A ULN focuses on efficiently streaming and encoding only the critical packet headers along with the application's message. In other words, while every Message Library can define its own outbound message encoding, the ULN variant is tailored for push-based messaging to a destination chain.

The ULN concept borrows from the idea of a Light Node in blockchain systems, which processes only block headers rather than entire blocks. Similarly, the ULN transmits a specific, optimized encoded format called the encodedPacket. This format is constructed in two key steps:

Message Encoding with ULN
Packet Header Encoding:
The ULN first creates a concise header containing vital routing and identification information. This includes:

Version Information: To ensure consistent interpretation of the packet.

Nonce: To maintain the correct order of messages.

Source and Destination Information: Such as endpoint identifiers and sender/receiver contract addresses.

This header functions as a roadmap for subsequent processing by workers.

Payload Encoding:
Next, the ULN encodes the remaining contents of the protocol packet. In this context:

The Application's Message: Represents the actual content sent by the application.

GUID: A global unique identifier that ties the message to its metadata.

The ULN combines these two components (packetHeader and payload) to create the final encodedPacket. This composite packet includes both the serialized header (providing essential metadata) and the payload (containing the GUID and the actual message), enabling downstream workers to efficiently process and verify the message.

You can see how these data structures differ under Message, Packet, and Payload.

Key Takeaways
Adaptability: The overall encoding process is flexible. Different Message Libraries can adopt their own strategies based on performance or security considerations. The ULN is just one example that emphasizes efficiency by transmitting minimal yet critical data.

Future-Proofing: This modular approach to encoding allows for technological advancements to be integrated into the protocol without disrupting existing application logic.

In Summary
Purpose: The Message Send Library manages the processes of encoding, configuring, and fee-calculating messages within the LayerZero protocol.

Function: Acting as a dedicated handler and routing contract, it bridges the gap between applications and the underlying message workers, ensuring proper packaging and delivery.

Design: By clearly separating responsibilities, the protocol remains modular and adaptable. The ULN exemplifies how a specialized Message Library can optimize for specific functions, such as ultra-lightweight packet header transmission.

User Benefit: For developers and end-users, this robust, configurable routing mechanism simplifies cross-chain communication while ensuring high efficiency and security.

Message Receive Library
The Message Receive Library is a core component of the LayerZero protocol that manages the reception and verification of messages on the destination chain. It functions as a dedicated message handler on the receive side by decoding incoming encoded packets, verifying their integrity through specialized processes, and routing valid messages to the endpoint.

What Is a Message Receive Library?
The Message Receive Library is responsible for several crucial tasks that enable secure and reliable processing of inbound messages:

Decoding Messages:
It parses the incoming data, ensuring the received packet information can be accurately reconstructed.

Verifying Integrity:
The library performs validation steps verifying that the packet is intended for the local endpoint and meets requirements set by the receiving application.

Managing and Enforcing Configuration:
Applications set configuration parameters via the LayerZero Endpoint, which are then applied to the library’s internal worker logic. This configuration determines the expected verification requirements.

info
Unlike the send side where fees are simply processed and workers selected, the receive library uses these settings to enforce that the workers verifying the packet match the predefined configuration.

Routing to the Endpoint:
After verification, the decoded packet is passed from the library to the endpoint for further processing.

In sum, the Message Receive Library encapsulates the core logic for safely accepting and processing incoming packets.

How It Fits Into the Protocol
LayerZero’s architecture separates the receive process into clear, sequential steps:

Receive Model Flow:
Workers → Message Receive Library → Endpoint → Application

Workers: These off-chain service providers receive the raw packet data and forward the encodedPacket to the destination chain.

Message Receive Library: The library decodes the incoming packet, verifies its integrity using both header information and payload data, and ensures that the encodedPacket meets library requirements and application configurations.

Endpoint: Once verified, the endpoint receives the validated packet and passes it to the appropriate application.

Application: The final recipient processes the application’s original message from the sender and executes business logic.

Receive Ultra Light Node (ULN)
A specialized variant of the Message Receive Library is the Receive Ultra Light Node (ULN). Like its sending counterpart, the Receive ULN is tailored for a streamlined process: it not only decodes and verifies inbound messages but also enforces that only the preconfigured DVNs (or workers) validate the message.

Message Processing with Receive ULN
Decoding the EncodedPacket:
The Receive ULN begins by decoding the received encodedPacket. This packet is composed of two parts:

Packet Header:
Contains vital routing and identification details, such as version information, nonce, source and destination endpoint IDs, and sender and receiver contract addresses.

Payload:
Includes the GUID and the actual application’s message.

You can see how these data structures differ under Message, Packet, and Payload.

Verifying DVN Submissions:
The Receive ULN allows DVNs to call its verification function verify(), where each DVN submits a verification for a specific packet header eand payload hash. Thse attestations are stored in an internal mapping, ensuring that each DVN’s submission is recorded.

Enforcing Configuration:
Before an inbound message is accepted, the Receive ULN retrieves the UlnConfig set by the application (via the Endpoint) and verifies that the DVN meet the required criteria, both in terms of identity and the number of block confirmations. This step ensures that only messages verified by the proper, preconfigured workers are processed.

Commit Verification:
Once the DVN verifications have been checked against the configuration, the commitVerification() function is called. This function:

Asserts that the packet header is correctly formatted and that the destination endpoint matches the local configuration.

Retrieves the receive UlnConfig based on the source endpoint and receiver contract address.

Checks that the necessary verification conditions have been met using the stored DVN verifications.

Reclaims storage for the verification records and calls the destination Endpoint's verify() method, thereby adding the message to the inbound messaging channel.

In Summary
Purpose: The Message Receive Library governs the decoding, verification, and routing of inbound messages in the LayerZero protocol.

Function: It deciphers the encodedPacket and validates the integrity through predefined checks, and then hands the message off to the endpoint for delivery.

Design: By isolating the inbound processing logic in a dedicated module, the protocol remains modular and adaptable. Specialized variants such as the Receive ULN demonstrate how the architecture can be tailored to meet different operational needs.

User Benefit: For developers and users, this clear separation ensures that cross-chain communication is both secure and efficient, while also remaining flexible enough to integrate future enhancements.

Message Read Library
The Read Library is a specialized Message Library designed for Omnichain Queries. It combines both send and receive capabilities to process read requests and deliver verified responses across chains.

What Makes the Read Library Unique?
Unlike the standard Message Send Library and Message Receive Library, the Read Library handles a full request-and-response workflow:

Send Side: It serializes a read command and directs it to the appropriate chain using the application's configured Decentralized Verifier Networks (DVNs).
Receive Side: It verifies DVN attestations for the returned data and routes the final response back to the endpoint and ultimately the requesting application.
This dual nature allows a single library to manage both outbound queries and inbound responses, ensuring the correct workers are used for each step.

How It Fits Into lzRead
When an application issues a query via EndpointV2.send(), the Read Library (ReadLib1002) encodes the request and forwards it to the configured DVNs. Each DVN reads from an archival node on the target chain, optionally performs off-chain compute (mapping or reducing data), and submits a hash of the result. Once the required number of DVNs confirm the same payload hash, the Read Library finalizes the response and the endpoint delivers the data to OApp.lzReceive().

This process transforms normal cross-chain messaging into a request/response pattern:

Application → Endpoint → Read Library → DVNs → Read Library → Endpoint → Application

Configuration and Security
Applications must configure the Read Library just like any other Message Library, specifying DVN thresholds and executor addresses. Because it enforces the DVN verification on the receive side, both the send and receive pathways must use the same ReadLib1002 instance to ensure correct processing.

Reference Implementation
The reference contract for the Read Library can be found in the LayerZero V2 repository:

LayerZero-v2/packages/layerzero-v2/evm/messagelib/contracts/uln/readlib/ReadLib1002.sol

This file details how queries are encoded, how DVN submissions are validated, and how fees are handled for workers and the treasury.

Summary
Purpose: Manage omnichain query requests and responses using the LayerZero Read workflow.
Function: Acts as both send and receive library, serializing requests, verifying DVN responses, and routing the final data to the application.
