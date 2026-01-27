"""
数据模型定义
定义策略文档的结构化输出格式
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class TopicCluster(BaseModel):
    """主题关键词簇"""
    name: str = Field(description="主题名称")
    keywords: List[str] = Field(description="关键词列表")
    target: str = Field(description="目标说明")


class TopicPriority(BaseModel):
    """主题优先级"""
    topic_name: str = Field(description="主题名称")
    score: int = Field(description="总分(0-40)", ge=0, le=40)
    reason: str = Field(description="推荐原因")


class ContentTemplate(BaseModel):
    """内容输出模板"""
    category: str = Field(description="模板类别(核心/次级/长尾)")
    title_formula: str = Field(description="标题公式")
    structure: List[str] = Field(description="内容结构")
    key_elements: List[str] = Field(description="关键要素")


class ExecutionPlan(BaseModel):
    """执行计划"""
    timeline: List[str] = Field(description="时间线(按月)")
    resources: List[str] = Field(description="资源需求")
    kpis: List[str] = Field(description="KPI指标")


class StrategyDocument(BaseModel):
    """策略文档结构"""
    # 元信息
    title: str = Field(description="文档标题")
    generated_at: str = Field(description="生成时间")
    business_scenario: str = Field(description="业务场景概述")

    # 受众分析
    target_audience: str = Field(description="目标受众描述")
    pain_points: List[str] = Field(description="关键痛点")
    decision_factors: List[str] = Field(description="决策因素")

    # 主题策略
    core_topics: List[TopicCluster] = Field(description="核心主题")
    secondary_topics: List[TopicCluster] = Field(description="次级主题")
    longtail_topics: List[TopicCluster] = Field(description="长尾主题")

    # 优先级
    priority_criteria: List[str] = Field(description="评分标准说明")
    priority_ranking: List[TopicPriority] = Field(description="优先级排序")

    # 模板
    templates: List[ContentTemplate] = Field(description="内容模板")

    # 执行
    execution: ExecutionPlan = Field(description="执行计划")

    # 附录
    notes: List[str] = Field(default_factory=list, description="注意事项")

    def to_markdown(self) -> str:
        """将结构化数据渲染为Markdown文档"""
        lines = [
            f"# {self.title}",
            "",
            f"> 生成时间：{self.generated_at}",
            f"> 业务场景：{self.business_scenario}",
            "",
            "---",
            "",
            "## 📋 目录",
            "1. 业务场景概述",
            "2. 目标受众分析",
            "3. 主题关键词簇",
            "4. 主题优先级逻辑",
            "5. 内容输出模板",
            "6. 执行计划",
            "7. 附录",
            "",
            "---",
            "",
            "## 1. 业务场景概述",
            "",
            self.business_scenario,
            "",
            "---",
            "",
            "## 2. 目标受众分析",
            "",
            f"**核心受众**：{self.target_audience}",
            "",
            "**关键痛点**：",
        ]

        for point in self.pain_points:
            lines.append(f"- {point}")

        lines.extend([
            "",
            "**决策因素**：",
        ])

        for factor in self.decision_factors:
            lines.append(f"- {factor}")

        lines.extend([
            "",
            "---",
            "",
            "## 3. 主题关键词簇",
            "",
            "### 3.1 核心主题（高价值、高转化）",
            "",
        ])

        for topic in self.core_topics:
            lines.append(f"- **{topic.name}** | 关键词：{', '.join(topic.keywords)} | 目标：{topic.target}")

        lines.extend([
            "",
            "### 3.2 次级主题（中等价值、扩大覆盖）",
            "",
        ])

        for topic in self.secondary_topics:
            lines.append(f"- **{topic.name}** | 关键词：{', '.join(topic.keywords)} | 目标：{topic.target}")

        lines.extend([
            "",
            "### 3.3 长尾主题（低竞争、精准触达）",
            "",
        ])

        for topic in self.longtail_topics:
            lines.append(f"- **{topic.name}** | 关键词：{', '.join(topic.keywords)} | 目标：{topic.target}")

        lines.extend([
            "",
            "---",
            "",
            "## 4. 主题优先级逻辑",
            "",
            "### 4.1 评分标准",
            "",
        ])

        for criteria in self.priority_criteria:
            lines.append(f"- {criteria}")

        lines.extend([
            "",
            "### 4.2 推荐执行顺序",
            "",
        ])

        for i, item in enumerate(self.priority_ranking, 1):
            lines.append(f"{i}. **{item.topic_name}**（{item.score}分）- {item.reason}")

        lines.extend([
            "",
            "---",
            "",
            "## 5. 内容输出模板",
            "",
        ])

        for template in self.templates:
            lines.extend([
                f"### 5.x {template.category}主题模板",
                "",
                f"**标题公式**：{template.title_formula}",
                "",
                "**内容结构**：",
            ])
            for j, item in enumerate(template.structure, 1):
                lines.append(f"{j}. {item}")
            lines.extend([
                "",
                f"**关键要素**：{', '.join(template.key_elements)}",
                "",
            ])

        lines.extend([
            "---",
            "",
            "## 6. 执行计划",
            "",
            "### 6.1 时间线",
            "",
        ])

        for item in self.execution.timeline:
            lines.append(f"- {item}")

        lines.extend([
            "",
            "### 6.2 资源需求",
            "",
        ])

        for item in self.execution.resources:
            lines.append(f"- {item}")

        lines.extend([
            "",
            "### 6.3 KPI指标",
            "",
        ])

        for item in self.execution.kpis:
            lines.append(f"- {item}")

        lines.extend([
            "",
            "---",
            "",
            "## 7. 附录",
            "",
            "### 7.1 注意事项",
            "",
        ])

        if self.notes:
            for note in self.notes:
                lines.append(f"- {note}")
        else:
            lines.append("- 本文档基于当前市场数据生成，建议定期更新")
            lines.append("- 执行过程中请根据实际效果调整策略")

        lines.extend([
            "",
            "---",
            "",
            "**文档结束**",
        ])

        return "\n".join(lines)


# JSON Schema 供 LLM 使用
STRATEGY_DOCUMENT_SCHEMA = StrategyDocument.model_json_schema()
