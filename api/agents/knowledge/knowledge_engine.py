"""
AcmeCorp Knowledge Engine

Intelligent retrieval system for company-specific Kubernetes knowledge.
Provides contextual documentation to AI agents for generating company-compliant solutions.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging


class AcmeCorpKnowledgeEngine:
    """
    Intelligent knowledge retrieval engine for AcmeCorp internal documentation.
    
    This engine provides AI agents with access to company-specific knowledge
    including standards, policies, approved resources, and incident procedures.
    """
    
    def __init__(self, knowledge_base_path: str = "internal_knowledge/"):
        self.logger = logging.getLogger(__name__)
        self.knowledge_path = Path(knowledge_base_path)
        self.documents = {}
        self.document_sections = {}
        
        # Initialize knowledge base
        self._load_all_documents()
        self._parse_document_sections()
        
        self.logger.info(f"Knowledge engine initialized with {len(self.documents)} documents")
    
    def _load_all_documents(self) -> None:
        """Load all markdown documents from the knowledge base."""
        try:
            for md_file in self.knowledge_path.glob("*.md"):
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents[md_file.stem] = content
                    self.logger.debug(f"Loaded knowledge document: {md_file.stem}")
                    
        except Exception as e:
            self.logger.error(f"Failed to load knowledge documents: {e}")
            # Create empty documents dict to prevent crashes
            self.documents = {}
    
    def _parse_document_sections(self) -> None:
        """Parse documents into sections for targeted retrieval."""
        for doc_name, content in self.documents.items():
            sections = self._extract_sections(content)
            self.document_sections[doc_name] = sections
            self.logger.debug(f"Parsed {len(sections)} sections from {doc_name}")
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from markdown content based on headers."""
        sections = {}
        current_section = "introduction"
        current_content = []
        
        lines = content.split('\n')
        for line in lines:
            # Check for section headers (# ## ###)
            if line.startswith('#'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.lstrip('#').strip().lower().replace(' ', '_')
                current_content = [line]  # Include the header
            else:
                current_content.append(line)
        
        # Save final section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
            
        return sections
    
    async def get_relevant_knowledge(self, issue_classification: Dict[str, Any]) -> str:
        """
        Retrieve relevant knowledge based on AI-classified issue.
        
        Args:
            issue_classification: Dictionary containing issue type, severity, components, etc.
            
        Returns:
            Formatted string containing relevant knowledge sections
        """
        issue_type = issue_classification.get("type", "unknown").lower()
        severity = issue_classification.get("severity", "medium").lower()
        components = [comp.lower() for comp in issue_classification.get("components", [])]
        root_cause = issue_classification.get("root_cause_category", "").lower()
        
        relevant_sections = []
        
        # Strategy: Match issue characteristics to knowledge sections
        
        # 1. Image-related issues
        if any(keyword in issue_type or keyword in root_cause for keyword in ["image", "pull", "registry"]):
            relevant_sections.extend(self._get_image_related_knowledge())
        
        # 2. Resource-related issues  
        if any(keyword in issue_type or keyword in root_cause for keyword in ["memory", "cpu", "resource", "crash", "oom"]):
            relevant_sections.extend(self._get_resource_related_knowledge())
        
        # 3. Network-related issues
        if any(keyword in issue_type or keyword in root_cause for keyword in ["network", "service", "dns", "connectivity"]):
            relevant_sections.extend(self._get_network_related_knowledge())
        
        # 4. Configuration-related issues
        if any(keyword in issue_type or keyword in root_cause for keyword in ["config", "env", "secret", "volume"]):
            relevant_sections.extend(self._get_configuration_related_knowledge())
        
        # 5. Always include incident procedures for high/critical severity
        if severity in ["high", "critical"]:
            relevant_sections.extend(self._get_incident_procedures())
        
        # 6. Always include approved resources for reference
        relevant_sections.extend(self._get_approved_resources_summary())
        
        # Remove duplicates and format
        unique_sections = list(dict.fromkeys(relevant_sections))  # Preserve order, remove dupes
        
        if not unique_sections:
            # Fallback: provide general troubleshooting guidance
            unique_sections = self._get_general_troubleshooting_knowledge()
        
        return self._format_knowledge_response(unique_sections)
    
    def _get_image_related_knowledge(self) -> List[str]:
        """Get knowledge sections related to container images."""
        sections = []
        
        # From standards document
        if "acmecorp_standards" in self.document_sections:
            sections.extend(self._extract_matching_sections("acmecorp_standards", [
                "container_image_policy",
                "approved_image_sources", 
                "image_naming_convention",
                "approved_base_images"
            ]))
        
        # From approved resources
        if "approved_resources" in self.document_sections:
            sections.extend(self._extract_matching_sections("approved_resources", [
                "container_images_registry",
                "web_frontend_images",
                "application_runtime_images",
                "deprecated/unapproved_images"
            ]))
        
        # From incident playbook
        if "incident_playbook" in self.document_sections:
            sections.extend(self._extract_matching_sections("incident_playbook", [
                "imagepullbackoff_investigation",
                "errimagepull_investigation"
            ]))
        
        return sections
    
    def _get_resource_related_knowledge(self) -> List[str]:
        """Get knowledge sections related to resource allocation and management."""
        sections = []
        
        # From standards
        if "acmecorp_standards" in self.document_sections:
            sections.extend(self._extract_matching_sections("acmecorp_standards", [
                "resource_allocation_standards",
                "frontend_application_tier",
                "backend_service_tier"
            ]))
        
        # From resource policies
        if "resource_policies" in self.document_sections:
            sections.extend(self._extract_matching_sections("resource_policies", [
                "compute_resource_tiers",
                "tier_1:_frontend_applications",
                "tier_2:_backend_services",
                "resource_allocation_principles"
            ]))
        
        # From incident playbook
        if "incident_playbook" in self.document_sections:
            sections.extend(self._extract_matching_sections("incident_playbook", [
                "crashloopbackoff_investigation",
                "out_of_memory_(oomkilled)_investigation",
                "cpu_throttling_investigation"
            ]))
        
        return sections
    
    def _get_network_related_knowledge(self) -> List[str]:
        """Get knowledge sections related to networking and connectivity."""
        sections = []
        
        # From standards
        if "acmecorp_standards" in self.document_sections:
            sections.extend(self._extract_matching_sections("acmecorp_standards", [
                "network_security_standards",
                "service_account_requirements"
            ]))
        
        # From incident playbook
        if "incident_playbook" in self.document_sections:
            sections.extend(self._extract_matching_sections("incident_playbook", [
                "network_and_connectivity_issues",
                "service_discovery_problems",
                "ingress_issues"
            ]))
        
        return sections
    
    def _get_configuration_related_knowledge(self) -> List[str]:
        """Get knowledge sections related to configuration and deployment."""
        sections = []
        
        # From approved resources
        if "approved_resources" in self.document_sections:
            sections.extend(self._extract_matching_sections("approved_resources", [
                "resource_configuration_templates",
                "configmap_templates",
                "secret_templates"
            ]))
        
        # From standards
        if "acmecorp_standards" in self.document_sections:
            sections.extend(self._extract_matching_sections("acmecorp_standards", [
                "namespace_organization",
                "required_labels",
                "required_annotations"
            ]))
        
        return sections
    
    def _get_incident_procedures(self) -> List[str]:
        """Get incident response procedures for high-severity issues."""
        sections = []
        
        if "incident_playbook" in self.document_sections:
            sections.extend(self._extract_matching_sections("incident_playbook", [
                "incident_classification",
                "immediate_investigation_steps",
                "resolution_procedures",
                "escalation_procedures"
            ]))
        
        return sections
    
    def _get_approved_resources_summary(self) -> List[str]:
        """Get summary of approved resources for quick reference."""
        sections = []
        
        if "approved_resources" in self.document_sections:
            sections.extend(self._extract_matching_sections("approved_resources", [
                "container_images_registry",
                "deprecated/unapproved_images"
            ]))
        
        return sections
    
    def _get_general_troubleshooting_knowledge(self) -> List[str]:
        """Fallback: get general troubleshooting guidance."""
        sections = []
        
        # Basic standards and procedures
        for doc_name in ["acmecorp_standards", "incident_playbook"]:
            if doc_name in self.document_sections:
                # Get first few sections as general guidance
                doc_sections = list(self.document_sections[doc_name].items())[:3]
                for section_name, content in doc_sections:
                    sections.append(content)
        
        return sections
    
    def _extract_matching_sections(self, document_name: str, section_patterns: List[str]) -> List[str]:
        """Extract sections that match given patterns from a document."""
        sections = []
        
        if document_name not in self.document_sections:
            return sections
        
        doc_sections = self.document_sections[document_name]
        
        for pattern in section_patterns:
            pattern_lower = pattern.lower()
            
            # Find matching sections (exact match or partial match)
            for section_name, content in doc_sections.items():
                if (pattern_lower == section_name or 
                    pattern_lower in section_name or 
                    section_name in pattern_lower):
                    sections.append(content)
                    break  # Only take first match for each pattern
        
        return sections
    
    def _format_knowledge_response(self, sections: List[str]) -> str:
        """Format knowledge sections into a coherent response."""
        if not sections:
            return "No relevant knowledge found in AcmeCorp documentation."
        
        formatted_response = "=== ACMECORP INTERNAL KNOWLEDGE BASE ===\n\n"
        
        for i, section in enumerate(sections, 1):
            # Add section separator
            formatted_response += f"--- Knowledge Section {i} ---\n"
            formatted_response += section
            formatted_response += "\n\n"
        
        formatted_response += "=== END ACMECORP KNOWLEDGE ===\n"
        
        return formatted_response
    
    def get_document_summary(self) -> Dict[str, Any]:
        """Get summary of loaded knowledge base for debugging."""
        summary = {
            "total_documents": len(self.documents),
            "documents": {},
            "total_sections": 0
        }
        
        for doc_name, sections in self.document_sections.items():
            summary["documents"][doc_name] = {
                "sections_count": len(sections),
                "section_names": list(sections.keys())
            }
            summary["total_sections"] += len(sections)
        
        return summary
    
    def search_knowledge(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search knowledge base for specific content.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of matching sections with metadata
        """
        results = []
        query_lower = query.lower()
        
        for doc_name, sections in self.document_sections.items():
            for section_name, content in sections.items():
                content_lower = content.lower()
                
                # Simple text matching (could be enhanced with fuzzy matching)
                if query_lower in content_lower:
                    # Calculate relevance score (simple word count)
                    relevance = content_lower.count(query_lower)
                    
                    results.append({
                        "document": doc_name,
                        "section": section_name,
                        "content": content,
                        "relevance": relevance
                    })
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:max_results]
