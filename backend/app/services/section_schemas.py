"""
TAD Section Schemas and Validation Rules

Defines the structure, requirements, and validation criteria for each TAD section.
Used by Writer Agent and Reviewer Agent to ensure completeness and quality.
"""

from typing import Dict, List, Any
from enum import Enum


class SectionName(str, Enum):
    """TAD section identifiers"""
    EXECUTIVE_SUMMARY = "executive_summary"
    CONTEXT = "context"
    FUNCTIONAL_REQUIREMENTS = "functional_requirements"
    NON_FUNCTIONAL_REQUIREMENTS = "non_functional_requirements"
    CONSTRAINTS = "constraints"
    ASSUMPTIONS = "assumptions"
    RISKS = "risks"
    SOLUTION_OVERVIEW = "solution_overview"
    COMPONENT_DECOMPOSITION = "component_decomposition"
    HOSTING = "hosting"
    IDENTITY_ACCESS_MANAGEMENT = "identity_access_management"
    NETWORK_CONFIGURATION = "network_configuration"
    SECURITY_CONTROLS = "security_controls"
    DATA_MANAGEMENT = "data_management"
    MONITORING_OBSERVABILITY = "monitoring_observability"
    DISASTER_RECOVERY = "disaster_recovery"
    COST_ESTIMATION = "cost_estimation"
    DEPLOYMENT_STRATEGY = "deployment_strategy"
    ADRS = "adrs"


class ArtifactType(str, Enum):
    """Types of artifacts required in sections"""
    RESOURCE_GROUP_NAMES = "resource_group_names"
    VNET_NAMES = "vnet_names"
    SUBNET_NAMES = "subnet_names"
    SECURITY_GROUP_NAMES = "security_group_names"
    KEY_VAULT_NAMES = "key_vault_names"
    STORAGE_ACCOUNT_NAMES = "storage_account_names"
    RBAC_ROLES = "rbac_roles"
    SERVICE_PRINCIPALS = "service_principals"
    MANAGED_IDENTITIES = "managed_identities"
    NETWORK_TOPOLOGY = "network_topology"
    SECURITY_CONTROLS_LIST = "security_controls_list"
    TAGGING_TABLE = "tagging_table"
    COST_BREAKDOWN = "cost_breakdown"
    DEPLOYMENT_PIPELINE = "deployment_pipeline"
    MONITORING_METRICS = "monitoring_metrics"
    ADR_DECISIONS = "adr_decisions"


class RAGDomain(str, Enum):
    """RAG knowledge domains"""
    NAMING_RESOURCE_GROUPS = "naming.resource_groups"
    NAMING_VNETS = "naming.vnets"
    NAMING_SUBNETS = "naming.subnets"
    NAMING_SECURITY_GROUPS = "naming.security_groups"
    NAMING_KEY_VAULTS = "naming.key_vaults"
    NAMING_STORAGE = "naming.storage"
    GOVERNANCE_TAGGING = "governance.tagging"
    GOVERNANCE_RBAC = "governance.rbac"
    GOVERNANCE_SECURITY_BASELINE = "governance.security_baseline"
    ARCHITECTURE_NETWORK_SEGMENTATION = "architecture.network_segmentation"
    ARCHITECTURE_IAM_MODEL = "architecture.iam_model"
    ARCHITECTURE_REFERENCE_PATTERNS = "architecture.reference_patterns"


class SectionSchema:
    """Schema definition for a TAD section"""
    
    def __init__(
        self,
        name: SectionName,
        title: str,
        description: str,
        required_artifacts: List[ArtifactType],
        required_tables: List[str],
        required_rag_domains: List[RAGDomain],
        min_paragraphs: int,
        max_length: int,
        requires_mermaid: bool = False,
        subsections: List[str] = None
    ):
        self.name = name
        self.title = title
        self.description = description
        self.required_artifacts = required_artifacts
        self.required_tables = required_tables
        self.required_rag_domains = required_rag_domains
        self.min_paragraphs = min_paragraphs
        self.max_length = max_length
        self.requires_mermaid = requires_mermaid
        self.subsections = subsections or []


# TAD Section Schemas
TAD_SECTION_SCHEMAS: Dict[SectionName, SectionSchema] = {
    
    SectionName.EXECUTIVE_SUMMARY: SectionSchema(
        name=SectionName.EXECUTIVE_SUMMARY,
        title="1. Executive Summary",
        description="High-level overview of the solution, business context, and key architectural decisions",
        required_artifacts=[],
        required_tables=[],
        required_rag_domains=[],
        min_paragraphs=3,
        max_length=1500,
        requires_mermaid=False
    ),
    
    SectionName.CONTEXT: SectionSchema(
        name=SectionName.CONTEXT,
        title="2. Context and Background",
        description="Business context, stakeholders, current state, and project objectives",
        required_artifacts=[],
        required_tables=["stakeholders"],
        required_rag_domains=[],
        min_paragraphs=2,
        max_length=2000,
        requires_mermaid=False
    ),
    
    SectionName.FUNCTIONAL_REQUIREMENTS: SectionSchema(
        name=SectionName.FUNCTIONAL_REQUIREMENTS,
        title="3. Functional Requirements",
        description="Detailed functional requirements with priorities and acceptance criteria",
        required_artifacts=[],
        required_tables=["functional_requirements"],
        required_rag_domains=[],
        min_paragraphs=1,
        max_length=3000,
        requires_mermaid=False
    ),
    
    SectionName.NON_FUNCTIONAL_REQUIREMENTS: SectionSchema(
        name=SectionName.NON_FUNCTIONAL_REQUIREMENTS,
        title="4. Non-Functional Requirements",
        description="Performance, scalability, availability, security, and compliance requirements",
        required_artifacts=[],
        required_tables=["non_functional_requirements"],
        required_rag_domains=[RAGDomain.GOVERNANCE_SECURITY_BASELINE],
        min_paragraphs=1,
        max_length=3000,
        requires_mermaid=False
    ),
    
    SectionName.CONSTRAINTS: SectionSchema(
        name=SectionName.CONSTRAINTS,
        title="5. Constraints",
        description="Technical, organizational, and regulatory constraints",
        required_artifacts=[],
        required_tables=["constraints"],
        required_rag_domains=[],
        min_paragraphs=1,
        max_length=1500,
        requires_mermaid=False
    ),
    
    SectionName.ASSUMPTIONS: SectionSchema(
        name=SectionName.ASSUMPTIONS,
        title="6. Assumptions",
        description="Key assumptions made during architecture design",
        required_artifacts=[],
        required_tables=[],
        required_rag_domains=[],
        min_paragraphs=1,
        max_length=1000,
        requires_mermaid=False
    ),
    
    SectionName.RISKS: SectionSchema(
        name=SectionName.RISKS,
        title="7. Risks and Mitigations",
        description="Identified risks with mitigation strategies",
        required_artifacts=[],
        required_tables=["risks"],
        required_rag_domains=[],
        min_paragraphs=1,
        max_length=2000,
        requires_mermaid=False
    ),
    
    SectionName.SOLUTION_OVERVIEW: SectionSchema(
        name=SectionName.SOLUTION_OVERVIEW,
        title="8. Solution Overview",
        description="High-level architecture overview with system context diagram",
        required_artifacts=[],
        required_tables=[],
        required_rag_domains=[RAGDomain.ARCHITECTURE_REFERENCE_PATTERNS],
        min_paragraphs=3,
        max_length=2500,
        requires_mermaid=True
    ),
    
    SectionName.COMPONENT_DECOMPOSITION: SectionSchema(
        name=SectionName.COMPONENT_DECOMPOSITION,
        title="9. Component Decomposition",
        description="Detailed component breakdown with Azure services, SKUs, and dependencies",
        required_artifacts=[],
        required_tables=["components"],
        required_rag_domains=[],
        min_paragraphs=2,
        max_length=4000,
        requires_mermaid=True
    ),
    
    SectionName.HOSTING: SectionSchema(
        name=SectionName.HOSTING,
        title="9.a. Hosting",
        description="Resource Groups, Azure regions, tagging strategy, and resource organization",
        required_artifacts=[
            ArtifactType.RESOURCE_GROUP_NAMES,
            ArtifactType.TAGGING_TABLE
        ],
        required_tables=["resource_groups", "tags"],
        required_rag_domains=[
            RAGDomain.NAMING_RESOURCE_GROUPS,
            RAGDomain.GOVERNANCE_TAGGING
        ],
        min_paragraphs=2,
        max_length=3000,
        requires_mermaid=False,
        subsections=["Resource Groups", "Tagging Strategy", "Regional Deployment"]
    ),
    
    SectionName.IDENTITY_ACCESS_MANAGEMENT: SectionSchema(
        name=SectionName.IDENTITY_ACCESS_MANAGEMENT,
        title="9.h.i. Identity and Access Management",
        description="Entra ID security groups, RBAC roles, service principals, and managed identities",
        required_artifacts=[
            ArtifactType.SECURITY_GROUP_NAMES,
            ArtifactType.RBAC_ROLES,
            ArtifactType.SERVICE_PRINCIPALS,
            ArtifactType.MANAGED_IDENTITIES
        ],
        required_tables=["security_groups", "rbac_assignments", "service_principals"],
        required_rag_domains=[
            RAGDomain.NAMING_SECURITY_GROUPS,
            RAGDomain.GOVERNANCE_RBAC,
            RAGDomain.ARCHITECTURE_IAM_MODEL
        ],
        min_paragraphs=3,
        max_length=4000,
        requires_mermaid=True,
        subsections=["Entra ID Security Groups", "RBAC Roles", "Service Principals", "Managed Identities"]
    ),
    
    SectionName.NETWORK_CONFIGURATION: SectionSchema(
        name=SectionName.NETWORK_CONFIGURATION,
        title="9.i.ii. Network Configuration",
        description="VNets, subnets, NSGs, private endpoints, and network topology",
        required_artifacts=[
            ArtifactType.VNET_NAMES,
            ArtifactType.SUBNET_NAMES,
            ArtifactType.NETWORK_TOPOLOGY
        ],
        required_tables=["vnets", "subnets", "nsgs"],
        required_rag_domains=[
            RAGDomain.NAMING_VNETS,
            RAGDomain.NAMING_SUBNETS,
            RAGDomain.ARCHITECTURE_NETWORK_SEGMENTATION
        ],
        min_paragraphs=3,
        max_length=4000,
        requires_mermaid=True,
        subsections=["Network Topology", "VNets and Subnets", "Network Security Groups", "Private Endpoints"]
    ),
    
    SectionName.SECURITY_CONTROLS: SectionSchema(
        name=SectionName.SECURITY_CONTROLS,
        title="10. Security Controls",
        description="Security baseline, encryption, key management, and compliance controls",
        required_artifacts=[
            ArtifactType.KEY_VAULT_NAMES,
            ArtifactType.SECURITY_CONTROLS_LIST
        ],
        required_tables=["security_controls", "encryption"],
        required_rag_domains=[
            RAGDomain.NAMING_KEY_VAULTS,
            RAGDomain.GOVERNANCE_SECURITY_BASELINE
        ],
        min_paragraphs=3,
        max_length=3500,
        requires_mermaid=False
    ),
    
    SectionName.DATA_MANAGEMENT: SectionSchema(
        name=SectionName.DATA_MANAGEMENT,
        title="11. Data Management",
        description="Data storage, retention, backup, and data lifecycle management",
        required_artifacts=[
            ArtifactType.STORAGE_ACCOUNT_NAMES
        ],
        required_tables=["storage_accounts", "backup_policy"],
        required_rag_domains=[
            RAGDomain.NAMING_STORAGE
        ],
        min_paragraphs=2,
        max_length=3000,
        requires_mermaid=False
    ),
    
    SectionName.MONITORING_OBSERVABILITY: SectionSchema(
        name=SectionName.MONITORING_OBSERVABILITY,
        title="12. Monitoring and Observability",
        description="Monitoring strategy, metrics, alerts, and logging",
        required_artifacts=[
            ArtifactType.MONITORING_METRICS
        ],
        required_tables=["monitoring_metrics", "alerts"],
        required_rag_domains=[],
        min_paragraphs=2,
        max_length=2500,
        requires_mermaid=False
    ),
    
    SectionName.DISASTER_RECOVERY: SectionSchema(
        name=SectionName.DISASTER_RECOVERY,
        title="13. Disaster Recovery and Business Continuity",
        description="DR strategy, RPO/RTO, backup procedures, and failover mechanisms",
        required_artifacts=[],
        required_tables=["dr_strategy"],
        required_rag_domains=[],
        min_paragraphs=2,
        max_length=2500,
        requires_mermaid=True
    ),
    
    SectionName.COST_ESTIMATION: SectionSchema(
        name=SectionName.COST_ESTIMATION,
        title="14. Cost Estimation",
        description="Estimated monthly costs per environment with breakdown by service",
        required_artifacts=[
            ArtifactType.COST_BREAKDOWN
        ],
        required_tables=["cost_breakdown"],
        required_rag_domains=[],
        min_paragraphs=1,
        max_length=2000,
        requires_mermaid=False
    ),
    
    SectionName.DEPLOYMENT_STRATEGY: SectionSchema(
        name=SectionName.DEPLOYMENT_STRATEGY,
        title="15. Deployment Strategy",
        description="CI/CD pipeline, IaC approach, deployment environments, and rollout plan",
        required_artifacts=[
            ArtifactType.DEPLOYMENT_PIPELINE
        ],
        required_tables=["deployment_environments"],
        required_rag_domains=[],
        min_paragraphs=2,
        max_length=2500,
        requires_mermaid=True
    ),
    
    SectionName.ADRS: SectionSchema(
        name=SectionName.ADRS,
        title="16. Architecture Decision Records (ADRs)",
        description="Key architectural decisions with context, options, and rationale",
        required_artifacts=[
            ArtifactType.ADR_DECISIONS
        ],
        required_tables=[],
        required_rag_domains=[],
        min_paragraphs=1,
        max_length=5000,
        requires_mermaid=False
    )
}


# Section ordering for TAD assembly
TAD_SECTION_ORDER = [
    SectionName.EXECUTIVE_SUMMARY,
    SectionName.CONTEXT,
    SectionName.FUNCTIONAL_REQUIREMENTS,
    SectionName.NON_FUNCTIONAL_REQUIREMENTS,
    SectionName.CONSTRAINTS,
    SectionName.ASSUMPTIONS,
    SectionName.RISKS,
    SectionName.SOLUTION_OVERVIEW,
    SectionName.COMPONENT_DECOMPOSITION,
    SectionName.HOSTING,
    SectionName.IDENTITY_ACCESS_MANAGEMENT,
    SectionName.NETWORK_CONFIGURATION,
    SectionName.SECURITY_CONTROLS,
    SectionName.DATA_MANAGEMENT,
    SectionName.MONITORING_OBSERVABILITY,
    SectionName.DISASTER_RECOVERY,
    SectionName.COST_ESTIMATION,
    SectionName.DEPLOYMENT_STRATEGY,
    SectionName.ADRS
]


def get_section_schema(section_name: SectionName) -> SectionSchema:
    """Get schema for a specific section"""
    return TAD_SECTION_SCHEMAS.get(section_name)


def get_all_section_schemas() -> Dict[SectionName, SectionSchema]:
    """Get all section schemas"""
    return TAD_SECTION_SCHEMAS


def get_section_order() -> List[SectionName]:
    """Get the ordered list of sections for TAD assembly"""
    return TAD_SECTION_ORDER
