Hi.. please wear a hat of an architect who will be laying foundational building blocks for internet for energy exchange.
This work needs balance betwen simplicity, performance, practicality and future adaptability. Remember that simplest network
that get the job done, are the most likely to be adopted at scale. We want to provide a thin glue layer between various (not all) existing energy exchange protocols targetting VPP, demand flexibility, EV charging, peer to peer tradin use cases.

I need you to study ./architecture folder. It contains the goal of architecture we would like to build.
It should enable decentralized energy exchange and fulfill following wish lists in that order:
1. Smart EV charging, at home rate based EV charging, destination EV charging, Demand flexibility, peer to peer energy 
   trading should naturally emerge as special cases of the above building blocks. To see how these use cases are handled now
   please study docs/implementation-guides/v2/EV_Charging_V0.8-draft.md  for EV charging, 
   docs/implementation-guides/v2/P2P_Trading/P2P_Trading_implementation_guide_draft.md  for P2P trading
   example jsons in  examples/ev_charging/ and examples/v2/P2P_Trading/ respectively.
   You can also study the existing schema in ../protocol-specifications-new/schema/Energy* and 
   ../protocol-specifications-new/schema/Ev* folders. 
2. It should be objective driven and give agency to sub-networks to maximize those objectives.
   Subnetworks are free to translate objectives/signals to say ieee2030.5 or openader or ocpi/ocpp/oscp based signals.
   But try to see that the toil in doing so is less. Enums that represent physical objects should not need to be reinvented,
   and external interfaces (e.g. market price signals) should be reused. The analogy, my friend gives is that of how http protocol
   allows mpge, gif objects to be embedded. We should have that kind of encapsulation.
   For objective driven flow, bid curve based economic aggregation & setpoint disaggregation is powerful concept. That should be 
   supported. See ref_docs/agentic_coordination_arch.md and ref_docs/product_compositions_with_DEG_Beckn_stack.md
3. The bi-lateral or multi-lateral contracts should be richly defined as a building block, and should allow trusted external signals (prices), 
   meter data (or cdrs charger data records) and any accumulated states (acumulated ) as inputs these they should allow unambiguous billing report documenting multi-party revenue flows (e.g. aggregator, customer, government (taxes), grid operator etc.).

The outcomes I am looking for are
1. Document in ./outputs folder on how the beckn building blocks should be extended to allow for these use cases? 
   Do we need more blocks?
   Are the building blocks simplest possible, in the sense that their combination creates emergennt complexity but each block/flow 
   (its api and schema) is simple and easy for anybody to understand.
2. Document in ./outputs folder with mermaid Sequence diagrams for each of use cases, reusing building blocks above.
3. Eventually down the road, I will need updated schemas in ../protocol-specifications-new/schema/Energy* folder 
   and examples json messages in ./outputs/example folder for composition between beckn core and Eenergy* schemas, using jsonld slots (Itemattributes, OfferAttributes, ContractAttributes etc.)

I know this is a huge ask.. I am not being lazy, and can act as a sounding board. Please ask. 
First can you show me how you will approach this task and your plan?




-------

Thanks! some answers to open questions:
- Bid curve aggregation can be done by new action existing ones cannot do it.
- Market clearing: Ok to add coordination layer, but if somehow it can emerge out of contract between each participant and market clearing agent, where prices are discovered not at the time of offer, but at synchronous confirmation stage at market clearing time, that would be even better.
- Grid nodes: yes, transformers can be energy resources too if somehow you can find they fit the pattern. I am not sure. They are owned by grid operator. They can decide locational price adder to keep flows within their constraints (e.g. limits on reverese flow) and also command offsets in case the price curve has a flat plateau.
- Forecast sharing: can be a seperate catalog item, or shared out of band to DERs.
- Settlement: feel free to debate this one and propose a path. I am not sure which existing onces you could extend.

With those, please proceed with pahse 1 or ask more questions.



