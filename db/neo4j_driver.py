# File: neo4j_driver.py
# This File handles all neo4j interactions for the exploitation script
from neo4j import GraphDatabase
from utils.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


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

    # Creates a new prompt node
    def get_or_create_prompt(self, prompt_id: str, text: str) -> str:
        cypher = '''
        MERGE (p:Prompt {id: $prompt_id})
        SET p.text = $text
        RETURN p.id AS id, p.text AS text
        '''
        with self._driver.session() as session:
            result = session.run(cypher, prompt_id=prompt_id, text=text)
            record = result.single()
            pid = record["id"] if record else None
        return pid

    # Creates a new response node
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
            rid = record["id"] if record else None
        return rid


    # Link a prompt to a chain
    def link_step(self, chain_id: str, prompt_id: str, step_number: int):
        cypher = '''
        MATCH (c:Chain {id: $chain_id}), (p:Prompt {id: $prompt_id})
        CREATE (c)-[:STEP {step_number: $step_number}]->(p)
        '''
        with self._driver.session() as session:
            session.run(cypher, chain_id=chain_id, prompt_id=prompt_id, step_number=step_number)

    # Link a result to a chain
    def link_result(self, prompt_id: str, response_id: str):
        cypher = '''
        MATCH (p:Prompt {id: $prompt_id}), (r:Response {id: $response_id})
        MERGE (p)-[:RESULTED_IN]->(r)
        '''
        with self._driver.session() as session:
            session.run(cypher, prompt_id=prompt_id, response_id=response_id)

    # Mark a chain as successful
    def mark_chain_success(self, chain_id: str, response_id: str):
        cypher = '''
        MATCH (c:Chain {id: $chain_id}), (r:Response {id: $response_id})
        MERGE (c)-[:ENDED_IN_SUCCESS]->(r)
        SET c.success = true
        '''
        with self._driver.session() as session:
            session.run(cypher, chain_id=chain_id, response_id=response_id)

    # Finds similar responses and recommends next best prompt for attack
    def suggested_next_prompt(self, embedding: list, bot_type: str, threshold: float = 0.7, limit: int = 1, n_neighbors_limit: int = 50) -> dict:
        cypher = '''
        CALL db.index.vector.queryNodes('responseEmbeddingIdx', $n_neighbors_limit, $embedding)
        YIELD node AS r, score AS similarity

        MATCH 
          (r)<-[:RESULTED_IN]-(p:Prompt)<-[s:STEP]-(c:Chain)<-[:TARGETED_IN]-(b:Bot {type: $bot_type})

        MATCH 
          (c)-[nextStep:STEP]->(nextPrompt:Prompt)

        WHERE
          similarity >= $threshold
          AND c.success = true
          AND nextStep.step_number = s.step_number + 1

        RETURN
          nextPrompt.id         AS prompt_id,
          nextPrompt.text       AS prompt_text,
          similarity

        ORDER BY similarity DESC
        LIMIT $limit
        '''
    
        with self._driver.session() as session:
            result = session.run(
                cypher,
                embedding=embedding,
                bot_type=bot_type,
                threshold=threshold,
                limit=limit,
                n_neighbors_limit=n_neighbors_limit
            )
            record = result.single()
        if record:
            return {
                "prompt_id": record["prompt_id"],
                "prompt_text": record["prompt_text"],
                "similarity": record["similarity"]
            }
        return None

    # Links created prompt to past prompt that was inspiration
    def link_reference(self, prompt_id: str, referenced_prompt_id: str):
        cypher = '''
        MATCH (p:Prompt {id: $prompt_id}), (ref:Prompt {id: $referenced_prompt_id})
        MERGE (p)-[:REFERENCED]->(ref)
        '''
        with self._driver.session() as session:
            session.run(
                cypher,
                prompt_id=prompt_id,
                referenced_prompt_id=referenced_prompt_id
            )