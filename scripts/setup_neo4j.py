#!/usr/bin/env python3
# Connects to Neo4j and creates the responseEmbeddingIdx vector index if it doesn't exist.

import time
from neo4j import GraphDatabase, basic_auth

from utils.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

# load connection info from env
uri = NEO4J_URI
user = NEO4J_USER
password = NEO4J_PASSWORD

# Cypher to create the index if missing
CREATE_INDEX_CYPHER = '''
CREATE VECTOR INDEX responseEmbeddingIdx IF NOT EXISTS
FOR (r:Response) ON (r.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
}
'''

# Poll until we can run a simple RETURN 1 query, or timeout
def wait_for_neo4j(driver, timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with driver.session() as session:
                session.run("RETURN 1").single()
            return True
        except Exception:
            time.sleep(1)
    return False

# Setup vector database to store response embedding info
def main():
    driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
    if not wait_for_neo4j(driver):
        print("Neo4j did not come up in time, exiting.")
        exit(1)

    with driver.session() as session:
        session.run(CREATE_INDEX_CYPHER)
        print("Vector index ensured.")

if __name__ == "__main__":
    main()
