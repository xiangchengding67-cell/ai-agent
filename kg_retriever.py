from neo4j import GraphDatabase

class ContractKnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_playbook_standard(self, clause_type):
        """
        根据条款类型从知识图谱中检索企业的标准条款和底线要求
        """
        query = """
        MATCH (c:ClauseType {name: $clause_type})-->(s:StandardTerm)
        OPTIONAL MATCH (c)-->(f:FallbackTerm)
        RETURN s.text AS standard, f.text AS fallback
        """
        with self.driver.session() as session:
            result = session.run(query, clause_type=clause_type)
            record = result.single()
            if record:
                return {
                    "standard": record["standard"],
                    "fallback": record["fallback"]
                }
            return None