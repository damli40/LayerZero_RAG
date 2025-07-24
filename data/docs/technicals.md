OApp Technical Reference
LayerZero’s Omnichain Application (OApp) standard defines a common set of patterns and interfaces for any smart contract that needs to send and receive messages across multiple blockchains. By inheriting OApp’s core functionality, higher-level primitives (such as OFT, ONFT, or any custom cross-chain logic) can rely on a unified, secure messaging layer.

All OApp implementations must handle:

Message sending: Encode and dispatch outbound messages
Message receiving: Decode and process inbound messages
Fee handling: Quote, collect, and refund native & ZRO fees
Peer management: Maintain trusted mappings between chains
Channel management and security: Control security and execution settings between chains
Deployment
Every OApp needs to be deployed on each chain where it will operate. Initialization involves two steps:

1. Integrate with the local Endpoint
Pass the local Endpoint V2 address into your constructor or initializer.
The Endpoint’s delegate authority is set to your OApp and the address initializing unless overridden.
As a delegate, your OApp can call any endpoint.* security method (setSendLibrary, setConfig, etc.) in a secure, authorized manner.
2. Configure peers (directional peering)
On each chain, the owner calls setPeer(eid, peerAddress) to register the remote OApp’s address for a given Endpoint ID.
Repeat on the destination chain: register the source chain’s OApp address under its Endpoint ID.
Because trust is directional, the receiving OApp checks peers[srcEid] == origin.sender before processing inbound messages.

Core Message Flow
OApps follow a three-step life cycle. Developers focus on local state changes and message encoding; LayerZero handles secure routing and final delivery.

1. send(...) Entrypoint
Developer-defined logic
Perform a local state change (e.g., burn or lock tokens, record intent).
Encode all necessary data (addresses, amounts, or arbitrary instructions) into a byte array.
Optionally accept execution options (gas limits, native gas transfers, or LayerZero Executor services).
Key points
Your public send(...) handles only local logic and message construction.
All packet assembly, peer lookup, and fee handling occur inside the internal call to endpoint.send(...).
2. Transport and Routing
Fee payment and validation
Ensure the caller has supplied exactly the required native or ZRO fee.
When endpoint.send(...) executes, the Endpoint verifies that the fees match the quote from the chosen messaging library. Underpayment causes a revert.
Packet construction and dispatch
The Endpoint computes the next outbound nonce for (sender, dstEid, receiver) and builds a Packet struct with nonce, srcEid, sender, dstEid, receiver, GUID, and the raw message.
It looks up which send library to use, either a per-OApp override or a default, for (sender, dstEid).
The send library serializes the Packet into an encodedPacket and returns a MessagingFee struct.
The Endpoint emits a PacketSent(...) event so DVNs and Executors know which packet to process.
DVNs & Executors
Paid DVNs pick up the packet, verify its integrity, and relay it to the destination chain’s Endpoint V2.
The destination library enforces DVN verification and block-confirmation requirements based on your receive config.
Destination Endpoint validation
Verify that the packet’s srcEid has a registered peer.
Confirm that origin.sender matches peers[srcEid].
Invoke lzReceive(...)
If validation succeeds, the destination Endpoint calls your OApp’s public lzReceive(origin, guid, message, executor, extraData).
3. lzReceive(...) Entrypoint
Access control and peer check
Only the Endpoint may call lzReceive.
Immediately validate that _origin.sender == peers[_origin.srcEid].
Internal _lzReceive(...) logic
Decode the byte array into original data types (addresses, amounts, or instructions).
Execute the intended on-chain business logic (e.g., mint tokens, unlock collateral, update balances).
If there’s a composable hook, your OApp can invoke sendCompose(...) to bundle further cross-chain calls.
Outcome
Upon completion, the destination chain’s state reflects the source chain’s intent. Any post-processing (events, composable calls) occurs here.
This clear separation between local state updates in send(...) versus remote updates in _lzReceive(...) lets you focus on business logic while LayerZero’s Endpoint V2 manages transport intricacies.

Security and Channel Management
Whether you’re using Solidity, Rust, or Move, these foundational patterns ensure consistent security, extensibility, and developer ergonomics.

Security and roles
Owner
Manages delegates, peers, and enforced gas settings
setPeer(...): update trust mappings
setDelegate(...): assign a new delegate for Endpoint configurations
setEnforcedOptions(...): define per-chain minimum gas for inbound execution
Delegate
Manages Endpoint settings and message-channel controls
setSendLibrary(oappAddress, eid, newLibrary): override send library for (oappAddress, eid).
setReceiveLibrary(oappAddress, eid, newLibrary, gracePeriod): override receive library; gracePeriod lets the previous library handle retries.
setReceiveLibraryTimeout(oappAddress, eid, library, newTimeout): update how long an old receive library remains valid.
setConfig(oappAddress, libraryAddress, params[]): adjust per-library settings (DVNs, Executors, confirmations).
skip(oappAddress, srcEid, srcSender, nonce): advance the inbound nonce without processing when verification fails.
nilify(oappAddress, srcEid, srcSender, nonce, payloadHash): treat the payload as empty and advance the inbound nonce.
burn(oappAddress, srcEid, srcSender, nonce, payloadHash): permanently discard a malicious or irrecoverable payload.
tip
Use multisigs or your preferred governance to manage Owner and Delegate roles.

Peering and Trust Management
peers mapping
Store a mapping from eid → bytes32 peerAddress. Using bytes32 lets you store addresses for various chains.
setPeer(eid, peerAddress) updates that mapping. Passing bytes32(0) disables the pathway.
Directional trust
Registering on Chain A → Chain B does not register the reverse. Each side must call setPeer for the other.
On receipt, enforce peers[origin.srcEid] == origin.sender to confirm the message is from the expected contract.
Updating peers
If you redeploy or upgrade an OApp, call setPeer on both old and new deployments to maintain continuity.

Omnichain Fungible Token (OFT) Technical Reference
LayerZero's Omnichain Fungible Token (OFT) standard enables a single fungible token to exist across many chains while preserving one global supply. The standard abstracts away differences in contract languages, so the high-level behavior is identical no matter which VM you deploy on.

Deployment
An OFT contract must be deployed on every network where a token currently exists or will exist. Since OFT contracts inherit all of the core properties of a LayerZero OApp, connecting OFT deployments requires setting a directional channel configuration between the source chain and the destination blockchain.

Channel Configuration
Every OFT deployment must have a directional channel configuration for messaging to be successful. This means the deployer must:

Connect the messaging channel at the Endpoint level (establishing the underlying pathway for cross-chain messages).
Pair the OFT deployments at the OApp level using setPeer(...), so each contract knows its trusted counterpart on the destination chain.
For an overview of what a messaging channel is, see Message Channel Security. For a more thorough explanation of channel configuration and peer relationships, see the OApp Reference.

Core Transfer Flow
When an OFT transfer is initiated, the token balance on the source chain is debited. This either burns or locks the tokens inside the OFT contract, similar to an escrow account. A message is then sent via LayerZero to the destination chain where the paired OFT credits the recipient by minting or unlocking the same amount. This mechanism guarantees a unified supply across all chains.

Debit on the source chain
The sender calls the OFT's send(...) function, burning or locking an amount of tokens.

Message dispatch via LayerZero
The source OFT packages the transfer details into a LayerZero message and routes it through the protocol's messaging layer. LayerZero's messaging rails handle cross-chain routing, verification of the encoded message, and delivery of the message to the destination chain's receiver OFT contract.

Credit on the destination chain
The paired OFT receives the message and credits the recipient by minting new tokens or unlocking previously-held tokens. The total supply across all chains remains constant, since burned or locked tokens on the source chain are matched 1:1 with minted or unlocked tokens on the destination.

(Optional) Trigger a composing call
A composing contract uses the tokens received in a new transaction, delivered automatically by the LayerZero Executor, to trigger some state change (e.g., swap, stake, vote). For more details on how to implement composable OFT transfers, see Omnichain Composability.

Core Concepts
This section explains the fundamental design principles that make OFT a flexible, developer-friendly standard for fungible tokens.

1. Transferring Value Across Different VMs
When transferring tokens across different virtual machines, OFT needs to handle varying decimal precision between chains. This is managed through a few key concepts:

Local Decimals
Blockchains use integer mathematics to represent token amounts, avoiding floating-point precision issues. Each chain's recommended token standard stores tokens as integers but with different decimal place conventions to represent fractional units. For example:

EVM chains: ERC-20 tokens typically use 18 decimal places. What users see as "1.0 USDC" is stored on-chain as 1000000000000000000 (1 × 10^18) - the smallest unit often called "wei"
Solana: SPL tokens commonly use 6 or 9 decimal places. The same "1.0 USDC" would be stored as 1000000 (1 × 10^6) - the smallest unit of SOL called "lamports" (10^-9)
Aptos: Fungible Assets may use 6 or 8 decimal places depending on the asset
Without proper conversion, transferring the integer value 1000000000000000000 from an 18-decimal EVM chain to a 6-decimal Solana chain would result in an astronomically large amount instead of the intended 1 token. The localDecimals field tells the OFT contract how many decimal places that specific blockchain uses to represent the token's smallest units.

Shared Decimals
To ensure consistent value representation, every OFT declares a sharedDecimals parameter. Before sending a token cross-chain, the OFT logic converts the "local" amount into a normalized "shared" unit. Upon arrival, the destination OFT reconverts that shared unit back into the local representation of its own decimal precision.

Dust Removal
Before converting the local unit amount (amountLD) into the shared unit amount (amountSD), OFT implementations first "floor" the local amount to the nearest multiple of the conversion rate so that no remainder ("dust") is included in the cross-chain transfer.

The normalization process works as follows:

Compute the conversion rate:

d
e
c
i
m
a
l
C
o
n
v
e
r
s
i
o
n
R
a
t
e
  
=
  
10
 
(
localDecimals
−
sharedDecimals
)
decimalConversionRate=10 
(localDecimals−sharedDecimals)
 
Remove dust by flooring to that multiple (e.g., integer division on the EVM):

f
l
o
o
r
e
d
A
m
o
u
n
t
L
D
  
=
  
⌊
amountLD
decimalConversionRate
⌋
×
decimalConversionRate
flooredAmountLD=⌊ 
decimalConversionRate
amountLD
​
 ⌋×decimalConversionRate
Compute and return the dust remainder to the sender:

d
u
s
t
  
=
  
amountLD
  
−
  
flooredAmountLD
dust=amountLD−flooredAmountLD
That dust is refunded to the sender's balance before proceeding with debiting the sender's account, and the flooredAmountLD is now used as the amountLD.

Convert the amount in local decimals (amountLD) to shared units on the source chain:

a
m
o
u
n
t
S
D
=
a
m
o
u
n
t
L
D
d
e
c
i
m
a
l
C
o
n
v
e
r
s
i
o
n
R
a
t
e
amountSD= 
decimalConversionRate
amountLD
​
 
Transmit the amount in shared decimals (amountSD) as part of the LayerZero message.

On the destination chain, reconstruct the local amount (amountLD):

a
m
o
u
n
t
L
D
=
a
m
o
u
n
t
S
D
∗
d
e
c
i
m
a
l
C
o
n
v
e
r
s
i
o
n
R
a
t
e
amountLD=amountSD∗decimalConversionRate
Why This Matters

Consistent Economic Value: "1 OFT" means the same thing on any chain, regardless of differing decimal precision.
DeFi Compatibility: Prevents rounding errors and ensures seamless integration with on-chain tooling (e.g., AMMs, lending protocols) that expect familiar decimal behavior.
No Precision Loss: By using a common sharedDecimals, you avoid truncation or expansion mistakes when moving large or small amounts across networks.
caution
If you override the vanilla sharedDecimals amount or have an existing token supply exceeding 18,446,744,073,709.551615 tokens, extra caution should be applied to ensure amountSD and amountLD do not overflow. Vanilla OFTs can disregard this admonition.

Shared‐Unit Overflow (amountSD)
OFT encodes amountSD as a 64-bit unsigned integer (uint64). The largest representable shared‐unit value is 2^64 − 1. Therefore, the maximum token supply (in whole‐token terms) is:

2
64
−
1
10
 
sharedDecimals
10 
sharedDecimals
 
2 
64
 −1
​
 
In vanilla OFT implementations, sharedDecimals = 6, yielding a max supply of

2
64
−
1
10
6
  
=
  
18,446,744,073,709.551615
 tokens
10 
6
 
2 
64
 −1
​
 =18,446,744,073,709.551615 tokens
If you choose a smaller sharedDecimals, the divisor shrinks and you may exceed the uint64 limit when converting a large amountLD into amountSD.

Local‐Unit Overflow (amountLD)
On some chains (e.g., Solana's SPL Token or Aptos's Fungible Asset), the native token amount is also stored as a 64-bit unsigned integer (uint64). In those environments, the maximum local amount is 2^64 − 1. But because amountLD must be a multiple of

decimalConversionRate
  
=
  
10
(
localDecimals
−
sharedDecimals
)
decimalConversionRate=10 
(localDecimals−sharedDecimals)
 
If amountSD × decimalConversionRate would exceed 2^64 − 1, the reconstructed amountLD cannot fit in the native uint64 type.

To avoid both overflow risks:

Pick sharedDecimals so that your target maximum supply divided by 10^{sharedDecimals} is ≤ 2^64 − 1.
Verify each chain's local type (e.g., uint64 on Solana/Aptos or uint256 on most EVM chains) can accommodate the resulting amountLD (i.e., amountSD × decimalConversionRate must not exceed the local limit).
2. Adapter vs. Direct Patterns: Contract Structure & Bridge Logic
What Is "Direct" vs. "Adapter"?
Direct Pattern

The token contract itself contains all bridge logic (send/receive) along with standard token functions (mint, burn, transfer).
When a user initiates a cross-chain transfer, the token contract on the source chain invokes internal "debit" logic to burn tokens, packages the message, and sends it through LayerZero. On the destination chain, the same contract (deployed there) receives the message and invokes internal "credit" logic to mint new tokens.
Adapter Pattern

The token contract is separate from the bridge logic. Instead of embedding send/receive in the token, an adapter contract handles all cross-chain operations.
The adapter holds (locks) user tokens (or has burn and mint roles, e.g., "Mint and Burn Adapter") and communicates with a paired OFT contract on the destination chain, which mints/unlocks or transfers the equivalent amount to the recipient.
From the developer's perspective, the only requirement is that the adapter exists as a standalone contract; the original token contract remains unaware of LayerZero or cross-chain flows.
Key Distinctions
Separate vs. Combined

Direct: Token + bridge = single deployable.
Adapter: Token = unmodified existing contract; Bridge logic = standalone adapter contract.
Mint And Burn Adapter Example

Even though it uses mint/burn semantics, it is still an "Adapter" because the adapter contract, not the token contract itself, contains all LayerZero business logic.
The adapter delegates calls to mint or burn on a "wrapper" token or calls an interface on the underlying token, separating concerns without requiring the original token code to change.
User/Integrator Perspective

No Difference in UX: Users call a standard send function (or "transfer" wrapper) without caring whether the token is Direct or Adapter.
Meshability: Any two OFT-enabled contracts (Direct or Adapter) on different chains can interoperate. This means liquidity can span adapters and direct tokens seamlessly, making the system truly omnichain.
Implications for Asset Issuers
Direct Pattern Suits New Tokens

When launching a brand-new token, embedding OFT logic directly can save on contract count and gas.
Simplifies deployment paths since your token and cross-chain logic are co-located.
Adapter Pattern Suits Existing Tokens

If you already have an active ERC-20 (or SPL, or Move) token with liquidity and integrations, deploying an adapter contract lets you plug into OFT without migrating your token.
The adapter can implement mint and burn, lock and unlock, or any hybrid, as long as it abides by the OFT interface.
Access Control & Governance

Direct Token: You manage roles (Admin, Delegate) within a single contract.
Adapter + Token: You may need to coordinate roles and permissions across two deployables.
3. Extensibility & Composability
OFT's design prioritizes flexibility and extensibility, allowing developers to customize token behavior and build complex cross-chain applications. The standard provides hooks for custom logic and supports composable transfers that can trigger additional actions on the destination chain.

Hooks Around Debit/Credit
Beyond Value Transfer

Many applications require extra functionality during or after cross-chain value transfer for example:

Protocol Fees: Automatically deduct a small fee on each cross-chain transfer and route it to a treasury.
Rate Limiting: Applying a limit on the number of tokens that can be sent in a given time-interval.
Access Control: Enforce time-based or role-based restrictions, such as requiring KYC verification for large transfers.
Overrideable Functions

OFT's core _debit and _credit methods are declared virtual (or their equivalent in non-EVM languages), allowing developers to override them in custom subclasses/modules.
Inject additional checks or side effects (e.g., take fees off transfers, check for rate limits, or validate off-chain context) without rewriting the entire message flow.
Composability with LayerZero Messaging
Cross-Chain Value Transfer + Call
You can bundle arbitrary data with your OFT transfer. For example, trigger a staking action on the destination chain if a recipient stakes a minimum amount, or execute a cross-chain governance vote.
The OFT contract simply forwards any extra bytes as a composeMsg through LayerZero's endpoint. On the destination, your custom lzCompose(...) hook can decode and act on that arbitrary data and token transfer.
Security & Roles
OFTs inherit LayerZero's admin/delegate role model:

Owner

Sets required gas limit requests for execution.
Can peer new OApp contracts or remove peers in emergencies.
Delegate

Configures connected chain's and messaging channel properties (e.g., Message Libraries, DVNs, and executors).
Can pause or unpause cross-chain functionality in emergencies.
Best Practice: Use a multisig to manage both Owner and Delegate privileges.

