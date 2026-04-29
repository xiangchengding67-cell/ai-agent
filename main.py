import os
from kg_retriever import ContractKnowledgeGraph
from debate_graph import debate_app
from redline_generator import RedlineGenerator

# 配置您的 OpenAI API Key 和 Neo4j 凭证
os.environ = "your-openai-api-key"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "password"

def process_contract_clause(clause_type, original_text):
    print(f"--- 开始处理条款: [{clause_type}] ---")
    
    # 1. 知识图谱检索
    kg = ContractKnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASS)
    # 此处为演示，若数据库未连接，使用 Mock 数据
    try:
        playbook_data = kg.get_playbook_standard(clause_type)
        playbook_text = playbook_data["standard"] if playbook_data else "缺省标准：要求责任上限不超过合同总金额的100%。"
    except Exception as e:
        print("Neo4j 未连接，使用本地 Mock Playbook 数据...")
        playbook_text = "缺省标准：要求责任上限不超过合同总金额的100%，且拒绝承担间接损失。"
    finally:
        kg.close()

    # 2. 准备初始状态
    initial_state = {
        "original_clause": original_text,
        "clause_type": clause_type,
        "playbook_standard": playbook_text,
        "attacker_critique": "",
        "defender_rebuttal": "",
        "final_verdict": "",
        "revised_clause": ""
    }

    # 3. 运行多智能体博弈图
    print("AI 智能体正在进行红队攻击与防守博弈...")
    final_state = debate_app.invoke(initial_state)

    # 4. 生成红线比对结果
    redline_md = RedlineGenerator.generate_markdown_redline(
        original_text, 
        final_state["revised_clause"]
    )

    print("\n[审查结果]")
    print(f"进攻方意见: {final_state['attacker_critique']}")
    print(f"防守方意见: {final_state['defender_rebuttal']}")
    print("\n[红线批注 (Markdown格式)]")
    print(redline_md)

if __name__ == "__main__":
    # 测试案例：一份偏向供应方的责任限制条款
    test_clause = "乙方（供应商）对甲方遭受的任何间接损失、利润损失不承担赔偿责任。且在任何情况下，乙方的总赔偿责任上限为1000元人民币。"
    
    process_contract_clause("责任限制条款 (Limitation of Liability)", test_clause)