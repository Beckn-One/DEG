# P2P Energy Trading Devkit

Goal of this devkit is to enable a developer to test round trip Beckn v2.0 mock messages between all network actors (BAP, Prosumer BPP (called BPP for brevity), Utility BPP, see [implementation-guide](/docs/implementation-guides/v2/P2P_Trading/P2P_Trading_implementation_guide_draft.md)), on their local machine within a few minutes.

It is a *batteries included* sandbox environment that requires minimal setup, and has environment variables pre-configured, connections to Catalog Discovery Service and Dedi test registry service pre-configured, catalogs pre-filled (using [this](./postman/P2P-Trading-CDSupload-DEG.postman_collection.json) collection).

## Setup

1. Install [docker desktop](https://www.docker.com/products/docker-desktop) & run it in background.
2. Install [git](https://git-scm.com/downloads) ensure that git is added to your system path.
3. Install [postman](https://www.postman.com/downloads/)
4. Clone this repository using git command line interface and navigate to the install directory
```
git clone https://github.com/Beckn-One/DEG.git
cd DEG/testnet/p2p-energy-trading-devkit/install
```

## Test network

1. Spin up the containers using docker compose. Verify that the following containers are running: redis, onix-bap, onix-bpp, onix-utilitybpp, sandbox-bap, sandbox-bpp, sandbox-utilitybpp. You can also navigate to docker desktop and check the containers and their logs.
    ```
    docker compose -f ./docker-compose-adapter-p2p.yml up -d
    docker ps
    ```

2. Open postman and import the folder `DEG/testnet/p2p-energy-trading-devkit/postman` to import all the collections and environment variables.

3. Start by publishing a mock catalog to the catalog discovery service using the collection `P2P-Trading:CDSupload-DEG`.

4. Check if you can see this catalog via a BAP by using the collection `P2P-Trading:BAP-DEG/discover`. Note that this can be flaky and may timeout sometimes due to CDS unavailability. In that case try again.

5. Use the collection `P2P-Trading:BAP-DEG` (select, init, confirm, status queries) to test the round trip Beckn v2.0 mock messages between BAP and BPP. The query reponse will show an "Ack" message, and detailed `on_select`, `on_init`, `on_confirm`, `on_status` messages from BPP should be visible in the BAP logs.

6. Use the collection `P2P-Trading:BPP-DEG` (on_select, on_init, on_confirm, on_status) to test only the BPP to BAP trip Beckn v2.0 mock messages between BPP to BAP.

7. Use the collection `P2P-Trading:BPP-DEG` (cascaded_init) to test only the BPP to Utility BPP round trip Beckn v2.0 mock messages. The query reponse will show an "Ack" message, and detailed `on_init`, `on_confirm`, `on_status` messages from Utility BPP should be visible in the Prosumer BPP logs.

8. Use the collection `P2P-Trading:UtilityBPP-DEG` (cascaded_init) to test only the Utility BPP to prosumer BPP Beckn v2.0 mock messages. The query reponse will show an "Ack" message, and detailed `on_init`, `on_confirm`, `on_status` messages from Utility BPP should be visible in the Prosumer BPP logs.

9. Stop the containers using docker compose
    ```
    docker compose -f ./docker-compose-adapter-p2p.yml down
    ```

## Under the hood

1. BAP `discover` calls are routed to Catalog Discovery Service url `https://34.93.141.21.sslip.io/beckn` defined [here](./config/local-p2p-routing-BAPCaller.yaml)
2. Public keys from network participants are fetched from test Dedi registry `http://api.testnet.beckn.one/registry/dedi`, and are used to confirm that Beckn messages are sent by the trusted actor (and not by an imposter). The namespace and registry entries in Dedi are preconfigured in yaml files within config folder.
3. Routing rules within each actor are defined in config for [BAP](./config/local-p2p-bap.yaml), [BPP](./config/local-p2p-bpp.yaml), [Utility BPP](./config/local-p2p-utilitybpp.yaml).
4. Network between various actors is defined in docker-compose-adapter-p2p.yml
5. Variables are preconfigured to following values.
    | Variable Name               | Value                         | Notes                       |
    | :-------------------------- | :---------------------------- | :-------------------------- |
    | `domain`                    | `beckn.one:energy-trading`    |                             |
    | `version`                   | `2.0.0`                       |                             |
    | `bap_id`                    | `bap-energy-trading-001`      |                             |
    | `bap_uri`                   | `http://localhost:8081/beckn` |                             |
    | `bpp_id`                    | `bpp-energy-trading-001`      |                             |
    | `bpp_uri`                   | `http://localhost:8082/beckn` |                             |
    | `transaction_id`            | `txn-energy-001`              |                             |
    | `iso_date`                  | `2025-01-01T10:00:00Z`        |                             |
    | `utilitybpp_id`             | `bpp-utility-grid-001`        |                             |
    | `utilitybpp_uri`            | `http://localhost:8083/beckn` |                             |
    | `bpp_bapreceiver_uri`       | `http://localhost:8082/beckn` |                             |
    | `bap_adapter_url`           | `http://localhost:9091`       | BAP collection only         |
    | `bpp_adapter_url`           | `http://localhost:9092`       | BPP collection only         |
    | `bpp_adapter_bapcaller_url` | `http://localhost:9092/beckn` | BPP collection only         |
    | `utilitybpp_adapter_url`    | `http://localhost:9093`       | Utility BPP collection only |
    | `cds_url`                   | `http://localhost:8080/beckn` | CDS Upload collection only  |
