Workers in LayerZero V2
In the LayerZero V2 protocol, Workers serve as the umbrella term for two key types of service providers: Decentralized Verifier Networks (DVNs) and Executors.

Both play crucial roles in facilitating cross-chain messaging and execution by providing verification and execution services. By abstracting these roles under the common interface known as a worker, LayerZero ensures a consistent and secure method to interact with both service types.

What Are Workers?
Workers are specialized entities that interact with the protocol to perform essential functions:

Verification as a Service: Decentralized Verifier Networks (DVNs), verify the authenticity and correctness of messages or transactions across chains.

Execution as a Service: Executors are responsible for carrying out actions requiring gas or compute units (transactions) on behalf of applications once verification is complete.

These roles are unified under the Worker interface, meaning that whether a service provider is a DVN or an Executor, it interacts with the protocol using a standardized set of methods.

Common Responsibilities
Both DVNs and Executors share several common responsibilities managed through the Worker contract:

Price Feeds: Maintaining up-to-date pricing information relevant to transaction fees or service costs.

Fee Management: Handling fees associated with using the service, ensuring that both service providers and application owners have clear, consistent cost structures.

By consolidating these responsibilities, the protocol simplifies the integration of different types of service providers while maintaining security and performance standards.

The Role of the Protocol
EndpointV2 uses a MessageLibManager.sol contract, responsible for the configuration and management of off-chain workers. Key features include:

Application-specific configurations: Applications can select specific message libraries, allowing them to tailor the protocol’s behavior to meet their unique security and trust requirements.

Customizable settings: Developers can set configurations for how messages are processed within each library, determine which off-chain entities are responsible for handling message delivery, and handle payment for these services.

Decentralization and flexibility: Instead of forcing every application into a one-size-fits-all approach,LayerZero V2 provides the flexibility needed to configure off-chain workers in a way that best fits the application’s design and security model.

This architecture allows LayerZero V2 to provide robust, decentralized cross-chain communication while giving application developers the tools needed to fine-tune their security and operational parameters.

Security Stack (DVNs)
As mentioned in previous sections, every application built on top of the LayerZero protocol can configure a unique messaging channel.

This stack of multiple DVNs allows each application to configure a unique security threshold for each source and destination, known as X-of-Y-of-N.

In this stack, each DVN independently verifies the payloadHash of each message to ensure integrity. Once the designated DVN threshold has been reached, the message nonce can be marked as verified and inserted into the destination Endpoint for execution.

Each DVN applies its own verification method to check that the payloadHash is correct. Once the required DVNs and optionally a sufficient number of optional DVNs have confirmed the payloadHash, any authorized caller (for example, an Executor) can commit the message nonce into the destination Endpoint’s messaging channel for execution.

Verification Model
Each DVN can use its own verification method to confirm that the payloadHash correctly represents the message contents. This design allows application owners to tailor their Security Stack based on the desired security level and cost–efficiency tradeoffs. For an extensive list of DVNs available for integration, see DVN Addresses.

DVN Adapters
DVN Adapters enable the integration of third-party generic message passing networks, such as native asset bridges, middlechains, or other specialized verification systems. With DVN Adapters, applications can incorporate diverse security models into their Security Stack, broadening the spectrum of available configurations while still ensuring a consistent verification interface via the payloadHash.

Since “DVN” broadly describes any verification mechanism that securely delivers a message’s payloadHash to the destination Message Library, application owners have the flexibility to integrate with virtually any infrastructure that meets their security requirements.

Configuring the Security Stack
Every LayerZero Endpoint can be used to send and receive messages. Because of that, each Endpoint has a separate Send and Receive Configuration, which an OApp can configure per remote Endpoint (i.e., the messaging channel, sending to that remote chain, receiving from that remote chain).

For a configuration to be considered valid, the Send Library configurations on Chain A must match the Receive Library configurations on Chain B.

Default Configuration
For each new channel, LayerZero provides a placeholder configutation known as the default. If you provide no configuration settings, the protocol will fallback to the default configuration.

This default configuration can vary per channel, changing the placeholder block confirmations, the X‑of‑Y‑of‑N thresholds for verification, the Executor, and the message libraries.

What is a Dead DVN?

Since LayerZero allows for anyone to permissionlessly run DVNs, the network may occassionally add new chain Endpoints before the default providers (Google Cloud or Polyhedra) support every possible pathway to and from that chain.

A default configuration with a Dead DVN will require you to either configure an available DVN provider for that Send or Receive pathway, or run your own DVN if no other security providers exist, before messages can safely be delivered to and from that chain.

warning
Even if the default configuration presets match the settings you want to use for your application, you should always set your configuration, so that it cannot change. The LayerZero default is a placeholder configuration, and subject to change.

Executors
Executors provide Execution as a Service for omnichain messages, automatically delivering and executing calls on the destination chain according to specific resource settings provided by your OApp directly or via call parameters.

Automatic execution abstract away the complexity of managing gas tokens on different networks and invoking contract methods manually, enabling a more seamless cross-chain experience.

What "Execution" Means
In the LayerZero protocol, execution refers to the invocation of the LayerZero Endpoint methods on the destination chain after a message has been verified:

lzReceive(...): Delivers a verified message to the destination OApp, triggering its logic.

lzCompose(...): Delivers a composed message (e.g., nested calls) after the initial receive logic has triggered.

Both methods are permissionless on the endpoint contract, meaning anyone can call them once the message has been marked as verified.

Executors: Execution as a Service
While you could manually call lzReceive(...) or lzCompose(... ) and pay gas on the destination chain directly, Executors automate this process:

Quote in Source Token: Executors accept payment in the source chain's native token and calculate the cost to deliver the destination chain's gas token based on the instructions provided and a pricefeed formula.

Automatic Delivery: After verification, the Executor invokes the appropriate endpoint method (lzReceive(...) or lzCompose(...)) with the specified resources and message.

Native Token Supplier: Executors are responsible for sourcing the native gas token on the destination chain, making them a resource for users needing to convert chain-specific resources.

Fee for Service: Executors charge a fee for relaying and executing messages.

Permissionless Functions
Because the endpoint methods are open, your application remains decentralized and trust-minimized, as any party can run an Executor or call the endpoint directly.

Message Options
Use Message Options to pass execution instructions along with your payload. Available options include:

lzReceiveOption: Specify gas and msg.value when calling lzReceive(...).

lzComposeOption: Specify gas and msg.value when calling lzCompose(...).

lzNativeDropOption: Drop a specified amount of native tokens to a receiver on the destination.

lzOrderedExecutionOption: Enforce nonce-ordered execution of messages.

These options let you fine-tune gas usage and value transfers for each message type. More information can be found under Message Options.

Default vs. Custom Executors
Choose the executor strategy that fits your application:

Default Executor: Use the out-of-the-box implementation maintained by LayerZero Labs.

Custom Executor: Select from third-party Executors or deploy your own variant.

Build Your Own: Follow Build Executors to implement a bespoke message Executor.

No Executor: Opt out of automated execution entirely; users can manually call lzReceive(...) or lzCompose(...) via LayerZero Scan or a block explorer.

Transaction Pricing Model
LayerZero's transaction pricing model is designed to fairly distribute costs across the various components that enable secure, reliable cross-chain messaging. Understanding this model helps developers and users make informed decisions about gas allocation and fee optimization.

Why Cross-Chain Pricing is Complex
Traditional blockchain transactions occur within a single network where gas costs are predictable and uniform. Cross-chain messaging introduces unique challenges:

Source chains have no knowledge of destination chain state, gas prices, or execution requirements
Multiple networks with different native tokens, gas mechanisms, and pricing models must be coordinated
Off-chain infrastructure (DVNs and Executors) provides critical services that require compensation
Message execution on the destination must be funded upfront from the source chain
LayerZero's pricing model addresses these challenges through a transparent, component-based fee structure.

Four-Component Fee Structure
Every LayerZero transaction consists of four distinct cost elements:

1. Source Chain Transaction
The standard blockchain transaction fee paid to miners/validators on the source network for including your transaction in a block. This follows each chain's native fee mechanism (gas on Ethereum, compute units on Solana, etc.).

2. Security Stack Fees
Payment to your configured Decentralized Verifier Networks (DVNs) for verifying and attesting to your message. These fees:

Vary based on your security configuration (number and type of DVNs)
Scale with the complexity of verification required
Are split among your chosen verifier networks
3. Executor Fees
Compensation to Executors for delivering and executing your message on the destination chain. This covers:

Monitoring source chains for new messages
Submitting transactions on destination chains
Managing the operational infrastructure for reliable delivery
4. Destination Gas Purchase
The cost of purchasing destination chain gas tokens to fund your message execution. This is calculated by converting your specified gas amount from destination pricing to source chain tokens.

Cross-Chain Gas Conversion
Since you pay on the source chain but consume gas on the destination chain, LayerZero workers perform real-time conversion using market prices:

Source Chain Cost
=
gasUnits
×
dstGasPrice
×
dstTokenPrice
srcTokenPrice
Source Chain Cost=gasUnits×dstGasPrice× 
srcTokenPrice
dstTokenPrice
​
 
Where:

gasUnits: Amount of gas needed on destination chain (e.g., 200,000)
dstGasPrice: Gas price on destination chain (e.g., 50 gwei)
dstTokenPrice: USD price of destination chain's native token (e.g., $3,000 for ETH)
srcTokenPrice: USD price of source chain's native token (e.g., $1.50 for MATIC)
The formula works in two steps:

Calculate destination gas cost: gasUnits × dstGasPrice = cost in destination tokens
Convert to source tokens: Multiply by the price ratio to get equivalent cost in source tokens
Example Scenario
Sending from Polygon (MATIC) to Ethereum (ETH):

gasUnits: 200,000 units
dstGasPriceWei: 50 gwei
dstTokenPrice: ETH = $3,000
srcTokenPrice: MATIC = $1.50
Calculation:

Step 1: Calculate gas cost on destination chain
200,000 gas units × 50 gwei = 10,000,000 gwei = 0.01 ETH

Step 2: Convert to source chain tokens using price ratio
0.01 ETH × ($3,000 ETH ÷ $1.50 MATIC) = 0.01 × 2,000 = 20 MATIC

This ensures you pay the correct amount in your source chain's currency to fund execution on any destination chain.

Dynamic Pricing Factors
Several factors influence the final transaction cost:

Chain-Specific Variations
Gas mechanisms differ across chains (Ethereum's EIP-1559, Arbitrum's L2 fees, Solana's compute units)
Network congestion affects base gas prices
Token price volatility impacts cross-chain conversion rates
Security Configuration Impact
More DVNs increase verification costs but enhance security
Premium DVN services may charge higher fees
Custom security thresholds affect overall pricing
Execution Requirements
Complex contract logic requires more destination gas
Composed messages need additional execution allowances
Message size affects processing costs
Fee Estimation and Quotes
LayerZero provides on-chain quote mechanisms that calculate exact fees before message submission:

Quote Components
Native fee: Cost in the source chain's native token
LZ token fee: Alternative payment option using LayerZero's utility token
Real-time pricing: Updates based on current gas prices and token values
Payment Flexibility
Applications can choose between:

Native token payment: Using the source chain's gas token (ETH, MATIC, AVAX, etc.)
LZ token payment: Using LayerZero's cross-chain utility token for consistent pricing
Gas Profiling Considerations
Destination gas requirements vary significantly based on your application logic:

Typical Gas Ranges
Simple token transfers: 60,000-80,000 gas
Complex DeFi interactions: 200,000-500,000 gas
Multi-step composed operations: 300,000+ gas
Optimization Strategies
Profile your contracts on each target chain to understand actual consumption
Include gas buffers to account for network-specific variations
Test execution paths thoroughly to avoid failed deliveries
Monitor gas costs across different chains and adjust allocations accordingly
Best Practices
For Developers
Design gas-efficient contracts to minimize destination execution costs
Implement proper fee estimation in your application interfaces
Consider chain-specific optimizations for frequently used pathways
Plan for gas price volatility in your economic models
For Users
Understand total cost breakdown before initiating transactions
Consider timing transactions during periods of lower network congestion
Monitor cross-chain fee patterns to optimize transaction scheduling
Plan gas allocations based on the complexity of your destination operations
Economic Alignment
LayerZero's pricing model creates proper economic incentives:

Security providers are compensated for verification services
Infrastructure operators earn fees for reliable message delivery
Gas efficiency is rewarded through lower total costs
Fair pricing ensures each pathway pays for its actual resource consumption
This transparent, component-based approach ensures that cross-chain messaging costs reflect the true value provided by each part of the LayerZero ecosystem while maintaining predictable pricing for applications and users.