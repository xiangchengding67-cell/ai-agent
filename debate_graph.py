from typing import Dict, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 定义状态字典
class DebateState(TypedDict):
    original_clause: str
    clause_type: str
    playbook_standard: str
    attacker_critique: str
    defender_rebuttal: str
    final_verdict: str
    revised_clause: str

llm = ChatOpenAI(model="gpt-4", temperature=0)

def attacker_agent(state: DebateState):
    """进攻型审查智能体：寻找合同文本中的风险和陷阱"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个极其挑剔的红队法律审查员。找出以下对方起草的合同条款中对己方不利的风险、模糊定义或陷阱。"),
        ("user", "条款类型: {clause_type}\n原条款内容: {original_clause}\n请给出你的风险攻击报告。")
    ])
    chain = prompt | llm
    response = chain.invoke({"clause_type": state["clause_type"], "original_clause": state["original_clause"]})
    return {"attacker_critique": response.content}

def defender_agent(state: DebateState):
    """防守型 Playbook 智能体：基于企业知识图谱进行反驳"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是防守型合规律师。根据公司内部的 Playbook 标准，对审查员提出的风险进行辩护，判断风险是否在可接受范围内。"),
        ("user", "公司标准要求: {playbook_standard}\n审查员提出的风险: {attacker_critique}\n请给出你的辩护意见。")
    ])
    chain = prompt | llm
    response = chain.invoke({"playbook_standard": state["playbook_standard"], "attacker_critique": state["attacker_critique"]})
    return {"defender_rebuttal": response.content}

def judge_agent(state: DebateState):
    """判决与起草智能体：汇总博弈结果并生成修改建议"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是高级仲裁律师。综合进攻方和防守方的意见，结合原条款，输出一份最终的修订版条款文本。仅输出修订后的文本，不要多余的解释。"),
        ("user", "原条款: {original_clause}\n进攻方意见: {attacker_critique}\n防守方意见: {defender_rebuttal}\n请生成修订版条款。")
    ])
    chain = prompt | llm
    response = chain.invoke({
        "original_clause": state["original_clause"],
        "attacker_critique": state["attacker_critique"],
        "defender_rebuttal": state["defender_rebuttal"]
    })
    return {"revised_clause": response.content, "final_verdict": "已达成共识并完成修订"}

# 构建 LangGraph 状态图
workflow = StateGraph(DebateState)

# 添加节点
workflow.add_node("attacker", attacker_agent)
workflow.add_node("defender", defender_agent)
workflow.add_node("judge", judge_agent)

# 定义边（执行顺序）
workflow.add_edge("attacker", "defender")
workflow.add_edge("defender", "judge")
workflow.add_edge("judge", END)

# 设置入口点并编译图
workflow.set_entry_point("attacker")
debate_app = workflow.compile()