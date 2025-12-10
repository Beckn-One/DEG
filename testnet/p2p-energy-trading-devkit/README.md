# cd install
# Commands to bring up containers incrementally. Each line is an atomic service
# docker compose -f ./docker-compose-adapter-p2p.yml up -d redis onix-bap
# docker compose -f ./docker-compose-adapter-p2p.yml up -d redis onix-bpp
# docker compose -f ./docker-compose-adapter-p2p.yml up -d redis onix-utilitybpp
# docker compose -f ./docker-compose-adapter-p2p.yml up -d sandbox-bap sandbox-bpp sandbox-utilitybpp

# Command to start all containers defined in compose file (-f) in detached (run in background) mode (-d)
# docker compose -f ./docker-compose-adapter-p2p.yml up -d

# To stop all the containers
# docker compose -f ./docker-compose-adapter-p2p.yml down

