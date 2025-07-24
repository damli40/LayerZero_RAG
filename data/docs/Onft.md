Omnichain Tokens
LayerZero’s omnichain token standards provide a unified framework to transfer both fungible and non-fungible tokens across different blockchain networks. Regardless of whether the tokens are built on EVM, Solana, or Aptos (or other environments), the underlying design follows these core principles:

Unified Cross-Chain Transfer Mechanism
Generic message passing:
Both fungible (OFT) and non-fungible (ONFT) tokens rely on a common cross-chain messaging interface defined in the OApp Standard. This interface handles the sending and receiving of token transfer data between chains, abstracting away the underlying chain differences.

Endpoint as a bridge:
All cross-chain token transfers rely on the LayerZero Endpoint to route messages between chains. The endpoint handles service routing to the correct workers, fee management, and enforces the application's settings on the destination chain.

Consistent Supply and Ownership Semantics
Unified supply model:
For fungible tokens, the standard ensures that the token supply remains consistent across chains. On the sending side, tokens are either burned or locked—effectively removing them from circulation—while on the receiving side the same amount is minted or unlocked. This “movement” of tokens creates a unified global supply.
OFT Example

NFT Transfer Patterns:
Non-fungible tokens (NFTs) follow a similar pattern:
Burn & Mint: The NFT is burned on the source chain and re-minted on the destination chain.
Lock & Mint/Unlock: Alternatively, an adapter can “lock” an existing NFT and later “unlock” it on the destination, preserving the original asset while enabling cross-chain functionality.
Flexible Design Patterns
Direct vs. Adapter approaches:
Developers can choose between direct implementations where the token contract itself handles minting/burning and adapter patterns (where an intermediary or mint authority lock/burns tokens on one chain and unlock or mint them on another). Both approaches maintain unified supply and allow seamless cross-chain transfers.

Composable Execution:
The design supports “composed” messages. This means that after the core token transfer logic is executed, additional instructions or custom business logic can be triggered on the destination chain as a separate transaction, opening the door to advanced cross-chain use cases.

Robust Fee and Security Configuration
Fee estimation and payment:
A built-in fee quoting mechanism estimates the cost of cross-chain transfers. Whether you’re transferring fungible tokens or NFTs, the sender is provided with an accurate fee estimate that covers source chain gas, protocol fees, and destination chain execution.

Configurable execution options:
Both token standards allow developers to set execution options (such as gas limits or fallback configurations) and enforce them to guarantee that sufficient resources are provided for the transfer on the destination chain.

Administrative controls:
Robust access controls—through admin and delegate roles—ensure that only authorized parties can update configurations (such as peers, fee settings, security settings, and execution parameters), maintaining a high security standard for all cross-chain operations.

Seamless Developer Experience
Abstraction over VM differences:
Although the underlying implementations may differ between environments (e.g., Solidity for EVM, Rust/Anchor for Solana, or Move for Aptos), the core concepts remain identical. Developers can rely on the same mental model: send a message that deducts tokens on the source chain and credits them on the destination, all while using a unified interface.

Extensibility:
The design allows developers to extend or customize the token logic. Whether you need to add custom fee mechanisms, block certain addresses, or trigger additional events on token receipt, the standard’s modular approach makes it easy to integrate advanced features.