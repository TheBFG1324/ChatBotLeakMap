# File: neo4j_driver.py
# This File handles all neo4j interactions for the exploitation script
from neo4j import GraphDatabase
import logging
from utils.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

logger = logging.getLogger(__name__)

# Neo4jDriver class holds all functionality to interact and get information from local Neo4j database
class Neo4jDriver:
    def __init__(self):
        self._driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    # Closes the driver
    def close(self):
        self._driver.close()

    # Inserts a bot node
    def insert_bot(self, bot_id: str, name: str, type_: str, url: str):
        cypher = '''
        MERGE (b:Bot {id: $bot_id})
        SET b.name = $name,
            b.type = $type,
            b.url = $url
        '''
        with self._driver.session() as session:
            session.run(cypher, bot_id=bot_id, name=name, type=type_, url=url)
        logger.debug(f"Upserted Bot {{id={bot_id}}}")

    # Insert a chain node
    def create_chain(self, chain_id: str, bot_id: str, timestamp: str, temperature: float, mode: str):
        cypher = '''
        CREATE (c:Chain {
            id: $chain_id,
            timestamp: datetime($timestamp),
            temperature: $temperature,
            mode: $mode,
            success: false
        })
        WITH c
        MATCH (b:Bot {id: $bot_id})
        CREATE (b)-[:TARGETED_IN]->(c)
        '''
        with self._driver.session() as session:
            session.run(
                cypher,
                chain_id=chain_id,
                bot_id=bot_id,
                timestamp=timestamp,
                temperature=temperature,
                mode=mode
            )
        logger.debug(f"Created Chain {{id={chain_id}}} for Bot {{id={bot_id}}}")

    # Create a prompt node
    def get_or_create_prompt(self, prompt_id: str, text: str) -> str:
        cypher = '''
        MERGE (p:Prompt {id: $prompt_id})
        SET p.text = $text
        RETURN p.id AS id
        '''
        with self._driver.session() as session:
            result = session.run(cypher, prompt_id=prompt_id, text=text)
            record = result.single()
            prompt_id = record["id"] if record else None
        logger.debug(f"Upserted Prompt {{id={prompt_id}}}")
        return prompt_id

    # Create a response node
    def get_or_create_response(self, response_id: str, text: str, timestamp: str, embedding: list) -> str:
        cypher = '''
        MERGE (r:Response {id: $response_id})
        SET r.text = $text,
            r.timestamp = datetime($timestamp),
            r.embedding = $embedding
        RETURN r.id AS id
        '''
        with self._driver.session() as session:
            result = session.run(
                cypher,
                response_id=response_id,
                text=text,
                timestamp=timestamp,
                embedding=embedding
            )
            record = result.single()
            resp_id = record["id"] if record else None
        logger.debug(f"Upserted Response {{id={resp_id}}}")
        return resp_id

    # Link a prompt to a chain
    def link_step(self, chain_id: str, prompt_id: str, step_number: int):
        cypher = '''
        MATCH (c:Chain {id: $chain_id}), (p:Prompt {id: $prompt_id})
        CREATE (c)-[:STEP {step_number: $step_number}]->(p)
        '''
        with self._driver.session() as session:
            session.run(cypher, chain_id=chain_id, prompt_id=prompt_id, step_number=step_number)
        logger.debug(f"Linked Chain {{id={chain_id}}} -> Prompt {{id={prompt_id}}} at step {step_number}")

    # Link a result to a chain
    def link_result(self, prompt_id: str, response_id: str):
        cypher = '''
        MATCH (p:Prompt {id: $prompt_id}), (r:Response {id: $response_id})
        MERGE (p)-[:RESULTED_IN]->(r)
        '''
        with self._driver.session() as session:
            session.run(cypher, prompt_id=prompt_id, response_id=response_id)
        logger.debug(f"Linked Prompt {{id={prompt_id}}} -> Response {{id={response_id}}}")

    # Mark a chain as successful
    def mark_chain_success(self, chain_id: str, response_id: str):
        cypher = '''
        MATCH (c:Chain {id: $chain_id}), (r:Response {id: $response_id})
        MERGE (c)-[:ENDED_IN_SUCCESS]->(r)
        SET c.success = true
        '''
        with self._driver.session() as session:
            session.run(cypher, chain_id=chain_id, response_id=response_id)
        logger.info(f"Chain {{id={chain_id}}} marked successful at Response {{id={response_id}}}")

    # Finds the recommended best continuation
    def find_best_match(self, embedding: list, threshold: float, bot_type: str, limit: int = 1):
        cypher = '''
        WITH $embedding AS emb, $threshold AS t, $bot_type AS bt
        CALL db.index.vector.cosineSimilarity(
            'responseEmbeddingIdx', emb
        ) YIELD node AS r, similarity
        MATCH (r)<-[:RESULTED_IN]-(p:Prompt)<-[:STEP]-(c:Chain)
        WHERE similarity > t
          AND (c)-[:TARGETED_IN]->(:Bot {type: bt})
          AND c.success = true
        RETURN p.id AS prompt_id, similarity
        ORDER BY similarity DESC
        LIMIT $limit
        '''
        with self._driver.session() as session:
            result = session.run(
                cypher,
                embedding=embedding,
                threshold=threshold,
                bot_type=bot_type,
                limit=limit
            )
            record = result.single()
        match = dict(record) if record else None
        logger.debug(f"Best match for bot_type={bot_type}: {match}")
        return match