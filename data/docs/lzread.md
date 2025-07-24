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