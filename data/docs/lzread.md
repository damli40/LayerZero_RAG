Omnichain Queries (lzRead)
Omnichain Queries extend LayerZero’s cross-chain messaging protocol to enable smart contracts to request and retrieve on-chain state from other blockchains. With lzRead, developers aren’t limited to simply sending messages — they can now pull data from external sources, bridging the gap between disparate networks in a fast, secure, and cost-efficient manner.

What Is LayerZero Read?
Beyond messaging:
Traditional cross-chain messaging allows a contract to push state changes to another chain. Omnichain Queries, by contrast, let a contract pull information from other chains, acting like a universal query interface across multiple networks.

Universal query language:
lzRead is built around the idea of a Blockchain Query Language (BQL) — a standardized way to construct, retrieve, and process data requests across various chains and even off-chain sources. Whether you need real-time data, historical state, or aggregated information, lzRead provides the framework to ask for and receive exactly what you need.

Why Omnichain Queries Are Valuable
Access cross-chain data securely:
In a fragmented blockchain ecosystem, a smart contract on one chain can’t natively read data from another. lzRead fills that gap by using Decentralized Verifier Networks (DVNs) that securely fetch and verify data from target chains, ensuring trustless access to global state.

Instant and cost-efficient data retrieval:
By optimizing the request–response flow, lzRead minimizes on-chain gas costs and latency. Instead of incurring multiple round-trips and paying gas on several chains, lzRead’s design reduces the process to a single round of messaging on the source chain—leading to near-instant, final responses.

Enhanced developer flexibility:
Whether you’re building decentralized finance (DeFi) protocols that need real-time price feeds, cross-chain yield strategies, or decentralized identity solutions, lzRead’s framework gives you a flexible tool to integrate smart contract data from any blockchain without heavy infrastructure overhead.

How Omnichain Queries (lzRead) Work
Read Example

Request definition:
An application initiates a read request by constructing a query that defines what data to fetch, from which target chain, and at which block or time. This query is encoded into a standardized command using BQL semantics.

Sending the request:
The read request is dispatched through the LayerZero endpoint using a specialized message channel. Instead of sending an ordinary cross-chain message, the command specifies that it’s a query—indicating that a response (and not just a state change) is expected.

DVN data fetch and verification:
Decentralized Verifier Networks (DVNs) pick up the query, retrieve the requested data from an archival node on the target chain, and—if needed—apply off-chain compute logic (such as mapping or reducing responses) to process the data. Each DVN then generates a cryptographic hash of the result, ensuring data integrity.

Response handling:
Once the data is fetched and verified by the required number of DVNs, the LayerZero endpoint delivers the final response back to the original chain using the standard messaging workflow. The receiving contract processes the response in its _lzReceive() function, extracting and using the queried data as needed.

Custom processing and compute settings:
If additional processing is required, the framework supports compute logic to transform or aggregate the data before it reaches your contract—allowing you to customize exactly how the data is formatted and used.

Broad Impact Across Environments
Chain-agnostic data access:
Although the internal implementations might differ, the core principle remains the same across all supported blockchains. lzRead provides a universal method for querying any chain’s data, making cross-chain applications more integrated and interoperable.

Flexible, low-latency, and secure:
By reducing the interaction to a single round of messaging (often called an “AA” message pattern), lzRead offers both low latency and cost savings compared to traditional multi-step query processes. And because the verification of data is handled by DVNs and enforced through cryptographic hashing, the system maintains high security with minimal additional trust assumptions.

Conclusion
Omnichain Queries (lzRead) improve how smart contracts access external state. Rather than being limited to local data or relying on cumbersome multi-step processes, developers can now issue a simple query to retrieve verified data from any supported blockchain.

The best teams in crypto are going omnichain.

With lzRead, developers can request, transform, and access data from any chain, across time — in a single function call.

Built as a new data primitive, lzRead expands LayerZero’s messaging protocol, allowing applications to retrieve and compute onchain data from multiple networks without the costs — of subscription-based services or setting up internal servers. Now, any application can access historical and current data from any chain: simplifying complex, onchain queries for DeFi, governance, NFTs, and more.

Teams like Chaos Labs, Wintermute, Apechain, Agora, EigenLayer, Gelato, Ambient, and AltLayer are already researching and developing lzRead use cases to make omnichain data composable and accessible across crypto.

Here’s what they are building…

Own Your Ape on Ethereum, Use Your Ape on ApeChain
“Automatically prove ownership of your Bored & Mutant Apes thanks to lzRead by LayerZero, ON APECHAIN. The Yuga Labs implementation of lzRead, NFT Shadows, are soulbound tokens, allowing Apes to verify ownership — without leaving Ethereum.” — Apecoin

ApeChain is using lzRead to verify ownership of Bored & Mutant Apes on Ethereum across chains. With the integration of lzRead, “NFT Shadows” are created — soulbound tokens that act as onchain mirrors of mainnet NFTs, enabling omnichain functionality without bridging or transferring assets. These NFT Shadows reflect ownership directly from Ethereum to Apechain, providing a decentralized, trustless way to verify holdings.

Previously, ApeChain relied on a indexer run by Yuga Labs to sync these shadow tokens. With lzRead, this process is now fully decentralized and onchain. Updates to NFT Shadows are triggered and verified through direct lzRead requests from Ethereum, ensuring that BAYC ownership is consistently and securely synchronized on ApeChain. This setup allows developers on Apehcain to integrate verified ownership into their applications on ApeChain without relying on centralized infrastructure, delivering a more secure and flexible cross-chain experience for Ape holders.

Unbiased, Cross-Chain Data Verification with Edge AI Oracle and Wintermute
“With lzRead, we delivered real-time, unbiased outcomes across chains, setting a trusted foundation for decentralized markets.” — Omer Goldberg, Founder & CEO, Chaos Labs

“Proud to be among the first builders using @LayerZero_Core’s lzRead — a powerful new primitive that enables cross-chain data access.” — Wintermute

The need for reliable, bias-free data verification within high-stakes prediction markets is a growing need in crypto.

lzRead played a pivotal role in resolving the Wintermute 2024 U.S. election prediction market across Ethereum, Arbitrum, and Base, showcasing how decentralized infrastructure can deliver tamper-proof and transparent outcomes. Wintermute’s market for HARRIS and TRUMP tokens enabled participants to predict and settle on the election results, leveraging Chaos Labs’ Edge Oracle Network for real-time, verified data from sources like AP, NBC, and Fox News.

By using lzRead to coordinate the election resolution (reading across chains), OutcomeMarket achieved accuracy and consistency across networks — an example of how lzRead can support decentralized systems in complex, multi-chain environments.

Image: How LayerZero settled the election market
This collaboration ensured that the election market was not only accessible and permissionless but also maintained consistent, immutable records onchain and across chains, providing trust and transparency across networks.

Bringing Actively Service Providers to Any Chain with EigenLayer
“lzRead should enable us to bring Ethereum’s state directly to other chains efficiently, enabling any AVS service to be consumed elsewhere..” — Sreeram Kannan, EigenLayer

EigenLayer is researching with LayerZero to explore how the lzRead primitive can enable actively validated services (AVSs) to serve consumers on any chain supported by the LayerZero protocol. This feature allows AVSs to offer services across various chains, integrating them into different ecosystems.

Simplifying Onchain Governance with Agora
“With lzRead, we have a straightforward way to unify governance across chains, allowing all token holders to participate securely in decision-making.” — Kent Fenwick, CTO of Agora

As we head towards a rollup-centric world, and protocols have their governance tokens spread out across multiple chains, calculating voting power, resolving votes across chains, and relaying outcomes becomes more complex. For a governance platform like Agora, this can become even more complex across different client configurations. Agora uses lzRead to aggregate votes from token holders across different chains, creating a highly secure and streamlined governance process that includes all participants. By unifying votes across networks, lzRead enables token holders to contribute to governance decisions regardless of their preferred blockchain, simplifying cross-chain interactions for decentralized communities.

Streamlining Cross-Chain Automation for DeFi with Gelato
Gelato Web3 Functions are powerful. With them, apps can…

Track Real-Time Prices Across Chains: lzRead aggregates DEX prices across chains, with Gelato Web3 Functions automating updates for seamless monitoring.
Automate Asset Management: lzRead aggregates cross-chain portfolio data, while Gelato automatically handles rebalancing schedules, optimizing efficiency.
Seamless RWA Yield Distribution with Plume’s SkyLink
“SkyLink, powered by lzRead, lets us expand the accessibility of RWA yields via real-time streaming across all chains and abstracting asset management complexities. We’re excited to explore new primitives emerge for onchain decentralized finance in an omnichain world” — Teddy Pornprinya, co-founder of Plume.

Plume, an infrastructure hub for Real World Assets (RWAs), leverages lzRead to power its SkyLink protocol: a continuous, cross-chain yield streaming for tokenized RWAs. SkyLink uses lzRead to ensure fast, secure state updates, allowing investors on multiple blockchains to receive real-time yield distributions without bridging or custody complexities.

SkyLink creates mirrored YieldTokens on each target chain, so holders can passively accumulate yield and use these tokens across DeFi protocols on various chains as if they were native assets. The integration of lzRead simplifies RWA yield distribution. It creates liquidity and flexibility for investors to engage in cross-chain strategies like reinvestment and collateralization.

Bringing Transparency and Security to Treasury Operations with Ambient
As successful onchain businesses continue to fund and grow their treasuries, reporting and protecting them becomes increasingly important. For products like Ambient that work across several chains, a single source of truth to rely on is crucial.Ambient integrates lzRead to fetch total value locked (TVL) across chains, relaying this information directly to its own Treasury contract without relying on a centralized trust assumption. This process ensures that Ambient’s Treasury contract accurately reflects real-time TVL in two key ways:

Periodic Updates: lzRead fetches TVL regularly, accurate TVL within the Treasury is maintained.
Real-Time Adjustments: lzRead triggers on deposits or withdrawals to update TVL, Ambient calculates precise AMD token pricing and protects transaction integrity.
When rebalancing events occur across chains, Ambient manages TVL through epochs or temporary pauses, Transparency ensured and manipulation prevented.

Automated Rebalancing and Seamless Data Access with AltLayer
“With AltLayer’s DVN and keeper services, developers have seamless, automated access to the cross-chain data they need, combining security and efficiency.” — YQ, AltLayer

AltLayer expands lzRead’s capabilities by offering a full Decentralized Verifier Network (DVN) service and keeper functionality, providing smooth data access and task automation across chains. As a DVN partner, AltLayer supplies infrastructure that enables developers to access verified cross-chain data efficiently, without the overhead of multiple integrations.

With its keeper service, AltLayer supports automated data retrieval and task execution, combining DVN security with reliable automation for streamlined cross-chain interactions.

DVN Partners: Secure, Reliable Data
DVNs are central to lzRead as the entities that validate and, therefore, secure the data applications are requesting. lzRead launched with DVNs run by BCW, Nethermind, LayerZero Labs, Animoca/Blockdaemon, and Nocturnal, which are all running archival nodes.

As lzRead expands to new chains, additional DVNs will be required for data redundancy and performance across the ecosystem. DVNs provide scalable, reliable infrastructure, empowering applications to securely retrieve cross-chain data and operate in a trustless environment.

lzRead: Build New Things. Onchain. On Every Chain.
With lzRead as a new data primitive, crypto-native applications can use onchain data from everywhere to power complex business logic anywhere. From DeFi and governance to NFTs and cross-chain automation, lzRead empowers projects to tap into seamless, secure data across multiple chains.

By enabling easy access, verification, and computation of onchain data, lzRead is helping to build a fully connected blockchain ecosystem — one where applications can scale effortlessly, innovate faster, and create more robust user experiences. The future of omnichain is here, and lzRead is the data primitive that makes it possible.