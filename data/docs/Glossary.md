LayerZero V2 Glossary
This glossary defines and explains key LayerZero concepts and terminology.

Chain ID
The native blockchain identifier assigned by the network itself (for example, 1 for Ethereum Mainnet, 42161 for Arbitrum Mainnet). This is distinct from LayerZero's Endpoint ID (EID), which is the protocol's internal identifier used to route messages between chains. When interacting with the LayerZero protocol, you'll primarily work with EIDs rather than chain IDs.

See Endpoint for more details.

Channel / Lossless Channel
A dedicated message pathway in LayerZero defined by four specific components: the sender OApp (source application contract), the source endpoint ID, the destination endpoint ID, and the receiver OApp (destination application contract).

The channel maintains message ordering through nonce tracking, ensuring messages are delivered exactly once and in the correct sequence. For example, if a token bridge on Ethereum (sender OApp) is communicating with its counterpart on Arbitrum (receiver OApp), their messages flow through a unique channel distinct from all other application pathways between these chains.

Each channel maintains its own independent message sequence, allowing multiple applications to communicate across the same chain pairs without interference.

Compose / Composition
The ability to combine multiple cross-chain operations into a single transaction. Composition allows for complex cross-chain interactions while maintaining transaction integrity across multiple chains.

Escrow Account
An escrow account is a financial arrangement where a third party, holds funds or assets on behalf of another until specific conditions are met.

Vertical Composability

The traditional form of smart contract composability, where multiple function calls are stacked within a single transaction. In vertical composability, all operations must succeed together or the entire transaction reverts, providing atomic execution. For example, when a cross-chain token bridge receives tokens, it might atomically update balances, emit events, and trigger other contract functions. All these operations either complete successfully or fail together.

Horizontal Composability

LayerZero's unique approach to cross-chain composability using endpoint.sendCompose and ILayerZeroComposer. Unlike vertical composability, horizontal composability allows a receiving contract to split its execution into separate atomic pieces. Each piece can succeed or fail independently, removing the requirement for all-or-nothing execution. This enables more flexible cross-chain operations, as applications can handle partial successes and continue execution even if some components fail. For example, a cross-chain DEX might receive tokens in one atomic transaction, then initiate a separate composed transaction for performing the swap, allowing the token receipt to succeed even if the swap fails.

CPI (Cross Program Invocation)
A CPI in Solana is when one program calls the instruction of another program. For more, refer to the official Solana documentation

Destination Chain
The blockchain network that receives and processes a LayerZero message. The destination chain hosts the contract that will execute the received message's instructions through its lzReceive function.

DVN (Decentralized Verifier Network)
A network of independent verifiers that validate message integrity between chains. DVNs are part of LayerZero's modular security model, allowing applications to configure multiple verification schemes for their messages.

Endpoint
The core, immutable smart contract deployed on each blockchain that serves as the entry and exit point for LayerZero messages. The Endpoint provides standardized interfaces for sending, receiving, and configuring messages. It's the primary interface through which applications interact with LayerZero.

Endpoint ID
Endpoint ID (EID) is LayerZero's internal identifier used to route messages between chains. Each Endpoint contract has a unique EID for determining which chain's endpoint to send to or receive messages from. EID values have no relation to Chain ID values - since LayerZero spans both EVM and non-EVM chains, EIDs provide a unified addressing system across all supported blockchains.

When using LayerZero contract methods, you'll work with EIDs rather than native chain IDs. The EID numbering convention follows a structured pattern:

30xxx: Mainnet chains
40xxx: Testnet chains
To check if a LayerZero contract supports communication with another chain, use the isSupportedEid() method with the target chain's EID.

Executor
Ensures the seamless execution of messages on the destination chain by following instructions set by the OApp owner on how to automatically deliver omnichain messages to the destination chain.

An off-chain service that monitors message verification status and executes verified messages on destination chains when all required DVNs have verified the message. Executors handle gas payments and message delivery.

It's a permissionless service that can be run by any party.

GUID (Global Unique ID)
A unique identifier generated for each LayerZero message that combines the message's nonce, source chain, destination chain, and participating contracts. GUIDs ensure messages can be tracked across the network and prevent replay attacks.

Lazy nonce (lazy inbound nonce)
A mechanism that tracks the highest consecutively delivered message number for a channel. Messages can be verified out of order, but they can only be executed sequentially starting from the lazy nonce. All messages before the message with lazyNonce have been verified. This ensures lossless message delivery while allowing parallel verification.

LZ Config
The file that declares the configuration for the OApp. Configuration refers to things such as the pathways (connections), DVN (Security Stack), and more. In our examples, this file has the default name of layerzero.config.ts but its name can be arbitrary. When needed, the LayerZero CLI expects the LZ config file via the --oapp-config flag. Check out the LZ config in the OFT example.

lzCompose
First, see Compose to understand what composition is.

A function that enables horizontal composition by allowing a received message to trigger additional cross-chain messages. These composed messages are processed sequentially, creating chains of cross-chain operations.

lzRead
Allows an OApp to request, receive and compute data from another blockchain by specifying the target chain and the block from which the state needs to be retrieved (including all historical data).

lzReceive
The standard function implemented by LayerZero-compatible contracts to process incoming messages. When a message is delivered, the destination chain's Endpoint calls lzReceive on the target contract with the decoded message data.

lzSend
The primary function used by the sender OApp to send messages through LayerZero. OApps call endpoint.send() on their local Endpoint, providing the destination details and message payload. The function initiates the cross-chain messaging process.

Mesh Network
LayerZero's network topology where every supported blockchain can directly communicate with every other supported blockchain. This creates a fully connected network without requiring intermediate chains or bridges.

Message Library (MessageLib)
Smart contracts that handle message payload packing on the source chain and verification on the destination chain.

MessageLibs are immutable and append-only, allowing protocols to add new verification methods while preserving existing ones. The Ultra Light Node (ULN) is the default MessageLib.

Ultra-Light Node is an implementation of a Message Library.

Message Options
A required parameter in LayerZero transactions that specifies how messages should be handled on the destination chain. Message options must be provided either through enforced options configured at the application level or as explicit parameters in the transaction. These options control critical execution parameters like gas limits for lzReceive calls, composed message handling, and native token drops on the destination chain.

When calling functions like quote() or send(), the protocol will revert if no valid message options are present. This is a safety mechanism to ensure every cross-chain message has explicit instructions for its execution. Applications can enforce minimum gas requirements using OAppOptionsType3, which combines any user-provided options with the application's required settings. For example, an OFT contract might enforce minimum gas limits for token transfers while allowing users to specify additional gas for composed operations.

Nonce
A unique identifier for the message within specific messaging channel. Prevents replay attacks and censorship by defining a strong gapless ordering between all nonces in each channel. Each channel maintains its own independent nonce counter.

Difference between nonce and GUID:

Nonce is unique within a channel (between two endpoints) and sequential.
GUID is unique across all channels and is not sequential, allowing for tracking messages across the entire LayerZero network.
OApp (Omnichain Application)
A smart contract that implements LayerZero's messaging interface for cross-chain communication. The base contract type for building omnichain applications.

OFT (Omnichain Fungible Token)
Omnichain Fungible Token - A token standard that extends fungible token standards such as the EVM's ERC20, Solana's SPL / Token-2022, and Aptos' Fungible Asset, with LayerZero's messaging capabilities, enabling seamless token transfers across different blockchains. OFTs maintain a unified total supply across all chains while allowing tokens to be transferred between networks.

This standard works by debiting (burn / lock) tokens on the source chain whenever an omnichain transfer is initiated, sending a message via the protocol, and delivering a function call to the destination contract to credit (mint / unlock) the same number of tokens debited. This creates a unified supply across all networks LayerZero supports that the OFT is deployed on.

Vanilla OFTs will utilize burn and mint:

Vanilla OFT Diagram

OFT Adapter
An OFT Adapter enables an existing token (e.g. ERC-20, SPL token) to function as an OFT. The OFT Adapter contract serves as a lockbox for the original token.

OFT Adapters will utilize lock and mint:

OFT Adapter

OMP (Omnichain Messaging Protocol)
The core protocol that enables secure cross-chain communication. An OMP provides the fundamental messaging capabilities that higher-level applications build upon.

ONFT (Omnichain Non-Fungible Token)
Omnichain Non-Fungible Token - A token standard that extends ERC721 with LayerZero's messaging capabilities, enabling NFT transfers across different blockchains while maintaining their unique properties and ownership history.

Packet
The standardized formatted data structure for messages in LayerZero, containing the message payload along with routing and verification information. Packets include fields like nonce, source chain, destination chain and the actual message data.

Payload
The actual data being sent in a cross-chain LayerZero message. This could be token transfer information, function calls, or any other data the application needs to transmit between chains.

PDA (Program Derived Address)
A PDA is a Solana account owned by a program and derived using "seeds". Refer to the official Solana documentation.

Security Stack
The combination of MessageLib, DVNs, and other security parameters that an application configures for its cross-chain messages. Each application can (and should) customize its security stack to balance security, cost, and performance.

Source Chain
The blockchain from which a cross-chain message is being sent.

ULN (Ultra Light Node)
The default MessageLib in LayerZero that implements a flexible verification system using configurable DVN sets. ULN allows applications to specify required and optional verifiers along with confirmation thresholds.

Ultra Light Node 302 is a MessageLib for Endpoint V2 applications. Ultra Light Node 301 is a MessageLib for existing Endpoint V1 applications wanting to utilize the new Security Stack and Executor.

Wire / Wiring
"Wiring" in LayerZero refers to the process of connecting OApps across different blockchains to enable cross-chain communication. The process involves setting peer addresses between OApps, configuring DVNs, and message execution settings. All these actions are done via submitting transactions to the relevant contracts (e.g. OApp, Endpoint) on each chain. Once wired, contracts can send and receive messages between specific source and destination contracts.

Worker
A general term for offchain or onchain components that perform specific tasks in the LayerZero network, including executors and DVNs.

X of Y of N
A configurable security model pattern where:

X: This is the number of required DVNs — each one is a specific, non-fungible verifier network that must always verify a message.

Y: This is the total number of DVNs needed for a message to be considered verified. It includes the required DVNs (X) plus a set threshold of optional DVNs. Any of the optional DVNs can contribute toward this threshold since they are fungible; it doesn't matter which optional DVNs verify, as long as the required number is met.

N: This is the total pool of DVNs available for verification. It includes both the specific required DVNs (X) and all optional DVNs from which verification could be collected.

For example, consider a "1 of 3 of 5" setup:

X = 1: One specific DVN must always sign (non-fungible).

Y = 3: A total of three DVNs are required. Since one is the required DVN, you need 2 additional verifier networks from the optional group (which are fungible).

N = 5: The application has configured five DVNs in total available for verification (1 required, plus a threshold of 2 out of a pool of 4 optional, which totals to 5 DVNs in the stack).

In summary, "X of Y of N" means that out of a total pool (N) of DVNs, you must always have some specific DVN(s) (X) verify, and then you need additional verifications from the remaining pool (with any optional DVN counting) until you hit the overall threshold (Y).

In pratice, this is done by setting an array of required DVN contract addresses, an array of optional DVN addresses, and a threshold for the optional DVNs.

Delegate
An address that an Omnichain Application (OApp) authorizes to act on its behalf within LayerZero's protocol. Specifically:

Authorization: The OApp calls setDelegate(address _delegate), registering a delegate that can perform configuration changes.

Permissions: Once set, both the OApp itself and its Delegate are the only parties allowed to update LayerZero settings (e.g., security thresholds, channel configurations). Any unauthorized caller will revert with LZ_Unauthorized.

This ensures that each application can securely delegate configuration rights.

Shared Decimals
The "lowest common denominator" of decimal precision across all chains in the OFT system. It limits how many decimal places can be reliably represented when moving tokens cross‑chain.

Default: 6 (optimal for most use cases, since it still allows up to 2⁶⁴–1 units)

Override: If your total supply exceeds (2⁶⁴–1) / 10^6, you can override sharedDecimals() to a smaller value (e.g. 4), trading precision for a higher max supply.

/// @dev Lowest common decimal denominator between chains.
/// Defaults to 6, allowing up to 18,446,744,073,709.551615 units.
function sharedDecimals() public view virtual returns (uint8) {
    return 6;
}

Local Decimals
The number of decimal places a token natively supports on the source chain.

Example (EVM): Most ERC‑20s use 18 local decimals.

Example (Solana): Many SPL tokens use 9 local decimals.

Example (Aptos): Many Fungible Asset tokens use 9 local decimals.

Tokens on different VMs may use different integer sizes (e.g. uint256 vs uint64), so local decimals capture each chain's native precision.

Decimal Conversion Rate
The scaling factor used to "clean" a local‑decimal token amount down to the shared‑decimal precision before cross‑chain transfer, and to scale it back on the destination chain.

decimalConversionRate = 10^(localDecimals – sharedDecimals)

When you bridge a token, you scale down on the source chain to fit the shared precision, then scale up on the destination chain to restore your original decimals.

Compute the rate

For a typical ERC‑20: localDecimals = 18, sharedDecimals = 6 → rate = 10^12
Scale Down (remove "dust")

// integer division drops any extra decimals
uint256 sharedUnits = originalAmount / rate;

Example:

Original amount: 1.234567890123456789 tokens
(that's 1_234_567_890_123_456_789 wei)
sharedUnits = 1_234_567_890_123_456_789 / 10^12 = 1_234_567.890123456789 → 1 234 567
Bridge the "sharedUnits"

Now you have a safe uint64‑friendly number: 1 234 567
Scale Up (restore local decimals)

uint256 restored = sharedUnits * rate;

restored = 1_234_567 * 10^12 = 1_234_567_000_000_000_000 wei
Which is 1.234567000000000000 tokens on the destination chain.
tip
Always do the "scale down" after subtracting any fees, so you don't accidentally round away more than intended.

Dust
The tiny remainder that gets dropped when you scale a token amount down to the shared‑decimal precision. In other words, any fractional units smaller than 1 / rate (where rate = 10^(localDecimals – sharedDecimals)) become "dust."

Precision safety: By removing dust, you guarantee that every bridged amount fits within the shared-decimal limits of all chains.

Rounding loss: That leftover dust is returned to the sender, so you want to remove it after fees and before bridging to avoid accidentally rounding away more than intended.