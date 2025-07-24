LayerZero Endpoint
The LayerZero Endpoint is the immutable, permissionless protocol entrypoint for sending and receiving omnichain messages.

Every LayerZero message passes through the Endpoint. It not only ensures secure and exactly-once message processing, but also will be your home for managing messaging channels, configurations, and fees.

Below is an overview of the five core modules that comprise the Endpoint and the role each plays:

Endpoint Interface
The core interface defines the essential data structures and key functions used for transmitting messages between blockchains. It establishes:

Functionality	Description
Messaging Parameters	Defines the destination endpoint identifier, receiver address, message payload, and worker options.
Messaging Receipts	Returns a unique global identifier (GUID) and a nonce with each send call to track messages.
Key Methods	Implements the core methods quote, send, verify, and lzReceive that all applications and workers routinely use.
This interface guarantees every message is uniquely identified, correctly routed, and has its fees and security checks properly handled.

Message Channel Management
This module tracks and manages messages along each distinct communication pathway.

Functionality	Description
Nonce Tracking	Maintains gapless, monotonically increasing nonces per sender, receiver, and chain to enforce exactly‑once delivery.
Payload Hash Recording	Stores the verified hash of each message payload to ensure message integrity before execution.
State Management	Manages transitions (delivered, skipped, or burned) to maintain the channel’s integrity.
Together, these functions create a lossless communication pathway essential for reliable cross‑chain messaging.

Message Library Management
This module enables applications (OApps) to tailor the security threshold, finality, executor, and more.

Functionality	Description
Custom Library Selection	Allows an application to choose a specific messaging library for different operations (e.g., send versus read); defaults to the standard library if not set.
Worker Configuration	Configures off‑chain workers (e.g, DVNs X-of-Y-of-N and Executor address) and finality settings on a per‑channel basis.
This flexibility enables each application to customize its security and fee management settings rather than relying on a fixed validator set and standard.

Send Context and Reentrancy Protection
The Messaging Context module ensures:

Functionality	Description
Unique Send Context	Tags each outbound message with a combination of the destination endpoint and sender address, preventing reentrancy.
Reentrancy Guard	Implements a dedicated modifier to prevent overlapping message processing.
These features maintain the integrity of the messaging process, ensuring that each message is processed in isolation.

Message Composition
"Arbitrary runtime dispatch" refers to the ability of a virtual machine (like the EVM) to decide dynamically at runtime which function to call based on input data. Not every blockchain virtual machine supports this, which limits how dynamically contracts can interact.

The Messaging Composer provides a standardized way to compose and send follow‑up messages within multistep cross‑chain workflows.

Feature	Description
Standardized Composition	Stores a composed message payload on-chain, which can later be retrieved and passed to a callback via lzCompose.
Lossless, Exactly‑Once Delivery	Inherits the same guarantees as the core messaging functions, ensuring that each composed message maintains integrity and finality.
Fault Isolation	Decouples composed messages from primary transactions so that errors remain isolated, simplifying troubleshooting.
This module enables advanced cross‑chain interactions without compromising security or finality.

Summary
The LayerZero Endpoint is the single, immutable entry and exit point for cross‑chain messaging, built on five core modules:

Module	Primary Role
Core Interface	Defines foundational messaging structures and methods to ensure unique identification and proper routing.
Messaging Channel	Tracks nonces and payload hashes between senders and receivers, enforcing exactly‑once, lossless delivery.
Message Library Manager	Provides flexibility for applications to configure custom messaging libraries and worker settings.
Messaging Context	Supplies execution context and reentrancy protection to safeguard message processing.
Messaging Composer	Standardizes the composition and dispatch of follow‑up messages, enabling advanced cross‑chain workflows without compromising security.
Together, these modules guarantee that every message sent and received via LayerZero is processed securely, efficiently, and reliably; no matter which blockchain the message originates from or is delivered to.

Previous
Omnichain Mesh Network
