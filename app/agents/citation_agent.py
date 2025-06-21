from typing import List, Dict, Any, Tuple, Optional
import re
import json
from dataclasses import dataclass

from app.agents.base_agent import BaseAgent
from app.models.schemas import SearchResult
from app.core.prompts import CITATION_AGENT_PROMPT
from app.core.config import settings


@dataclass
class Citation:
    """Represents a citation to be inserted"""
    claim_text: str
    source_index: int
    source_url: str
    source_title: str
    confidence: float
    position: int  # Character position in text


class CitationAgent(BaseAgent):
    """Agent responsible for adding citations to research reports"""
    
    def __init__(self):
        super().__init__(
            model=settings.CITATION_MODEL,
            name="Citation Agent"
        )
        
    def get_system_prompt(self) -> str:
        return CITATION_AGENT_PROMPT
        
    async def add_citations(
        self, 
        report: str, 
        sources: List[SearchResult],
        findings: List[Dict[str, Any]] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Add citations to a research report
        
        Args:
            report: The research report text
            sources: List of sources used in the research
            findings: Optional list of specific findings with their sources
            
        Returns:
            Tuple of (cited_report, citation_list)
        """
        
        # First, create a source index
        source_index = self._create_source_index(sources)
        
        # Identify claims that need citations
        claims = await self._identify_claims(report)
        
        # Match claims to sources
        citations = await self._match_claims_to_sources(
            claims, 
            sources, 
            findings
        )
        
        # Insert citations into the report
        cited_report = await self._insert_citations(report, citations)
        
        # Generate citation list
        citation_list = self._generate_citation_list(citations, source_index)
        
        return cited_report, citation_list
        
    def _create_source_index(self, sources: List[SearchResult]) -> Dict[int, SearchResult]:
        """Create an index of sources for easy reference"""
        return {i + 1: source for i, source in enumerate(sources)}
        
    async def _identify_claims(self, report: str) -> List[Dict[str, Any]]:
        """Identify factual claims in the report that need citations"""
        
        # Split report into sentences for analysis
        sentences = self._split_into_sentences(report)
        
        # Batch sentences for efficient processing
        batch_size = 10
        all_claims = []
        
        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i + batch_size]
            batch_text = "\n".join([f"{j+1}. {sent}" for j, sent in enumerate(batch)])
            
            prompt = f"""
            Identify factual claims in these sentences that require citations.
            
            Sentences:
            {batch_text}
            
            For each sentence containing a factual claim, identify:
            1. The sentence number
            2. The specific claim that needs citation
            3. The type of claim (statistic, fact, quote, finding, comparison)
            4. How important citation is (high/medium/low)
            
            Skip:
            - General knowledge or common facts
            - Transitional sentences
            - Questions or hypotheticals
            - Section headers
            
            Output as JSON:
            {{
                "claims": [
                    {{
                        "sentence_num": 1,
                        "text": "...",
                        "claim": "specific claim text",
                        "type": "statistic|fact|quote|finding|comparison",
                        "importance": "high|medium|low"
                    }}
                ]
            }}
            """
            
            response = await self._call_llm(prompt, max_tokens=2000)
            
            try:
                # Extract JSON from response
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response[start_idx:end_idx]
                    data = json.loads(json_str)
                    
                    # Adjust sentence numbers to global position
                    for claim in data.get("claims", []):
                        claim["sentence_num"] = i + claim["sentence_num"] - 1
                        if claim["sentence_num"] < len(sentences):
                            claim["text"] = sentences[claim["sentence_num"]]
                        
                    all_claims.extend(data.get("claims", []))
                
            except Exception as e:
                print(f"Error parsing claims: {e}")
                continue
                
        return all_claims
        
    async def _match_claims_to_sources(
        self,
        claims: List[Dict[str, Any]],
        sources: List[SearchResult],
        findings: List[Dict[str, Any]] = None
    ) -> List[Citation]:
        """Match identified claims to appropriate sources"""
        
        citations = []
        
        # If we have findings with explicit source mappings, use those first
        finding_map = {}
        if findings:
            for finding in findings:
                fact = finding.get("fact", "")
                source_url = finding.get("source_url", "")
                if fact and source_url:
                    finding_map[fact.lower()] = source_url
                    
        # Process claims
        for claim in claims:
            # First check if this claim matches a known finding
            claim_text = claim["claim"].lower()
            matched_source = None
            
            # Check finding map
            for fact_text, source_url in finding_map.items():
                if self._text_similarity(claim_text, fact_text) > 0.7:
                    # Find the source index
                    for i, source in enumerate(sources):
                        if source.url == source_url:
                            matched_source = (i + 1, source, 0.9)
                            break
                    break
                    
            # If no direct match, search all sources
            if not matched_source:
                source_matches = await self._find_best_source_match(
                    claim,
                    sources
                )
                if source_matches:
                    matched_source = source_matches[0]
                    
            # Create citation if match found
            if matched_source:
                source_idx, source, confidence = matched_source
                
                # Find position in original text
                position = 0
                
                citations.append(Citation(
                    claim_text=claim["text"],
                    source_index=source_idx,
                    source_url=source.url,
                    source_title=source.title,
                    confidence=confidence,
                    position=position
                ))
                
        return citations
        
    async def _find_best_source_match(
        self,
        claim: Dict[str, Any],
        sources: List[SearchResult]
    ) -> List[Tuple[int, SearchResult, float]]:
        """Find the best source match for a claim"""
        
        # Create a batch prompt to evaluate all sources at once
        sources_summary = "\n\n".join([
            f"Source {i+1}:\nTitle: {s.title}\nURL: {s.url}\nContent: {s.snippet[:200]}..."
            for i, s in enumerate(sources[:5])  # Limit to first 5 sources
        ])
        
        prompt = f"""
        Match this claim to the most appropriate source.
        
        Claim: "{claim['claim']}"
        Type: {claim['type']}
        Full sentence: "{claim['text']}"
        
        Available sources:
        {sources_summary}
        
        Evaluate which sources best support this claim. Consider:
        1. Direct mention of the fact/statistic
        2. Relevance to the claim
        3. Authority of the source
        4. Specificity of the match
        
        Output as JSON:
        {{
            "matches": [
                {{
                    "source_num": 1,
                    "confidence": 0.9,
                    "reason": "..."
                }}
            ]
        }}
        
        Only include sources with confidence > 0.6.
        """
        
        response = await self._call_llm(prompt, max_tokens=1000)
        
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)
                matches = []
                
                for match in data.get("matches", []):
                    source_idx = match["source_num"]
                    if 1 <= source_idx <= len(sources):
                        matches.append((
                            source_idx,
                            sources[source_idx - 1],
                            match["confidence"]
                        ))
                        
                # Sort by confidence
                matches.sort(key=lambda x: x[2], reverse=True)
                return matches
            
        except Exception as e:
            print(f"Error parsing source matches: {e}")
            
        return []
            
    async def _insert_citations(
        self,
        report: str,
        citations: List[Citation]
    ) -> str:
        """Insert citations into the report text"""
        
        # Group citations by claim to handle multiple sources
        claim_citations = {}
        for citation in citations:
            key = citation.claim_text
            if key not in claim_citations:
                claim_citations[key] = []
            claim_citations[key].append(citation)
            
        # Process the report
        cited_report = report
        processed_claims = set()
        
        for claim_text, cite_list in claim_citations.items():
            if claim_text in processed_claims:
                continue
                
            # Find all occurrences of this claim in the report
            if claim_text in cited_report:
                # Build citation string
                if len(cite_list) == 1:
                    citation_str = f" [{cite_list[0].source_index}]"
                else:
                    # Multiple sources
                    indices = sorted(set(c.source_index for c in cite_list))
                    citation_str = " [" + ",".join(str(i) for i in indices) + "]"
                    
                # Replace the claim with claim + citation
                cited_report = cited_report.replace(
                    claim_text, 
                    claim_text + citation_str,
                    1  # Only replace first occurrence
                )
                
            processed_claims.add(claim_text)
            
        return cited_report
        
    def _generate_citation_list(
        self,
        citations: List[Citation],
        source_index: Dict[int, SearchResult]
    ) -> List[Dict[str, Any]]:
        """Generate a formatted citation list"""
        
        # Get unique sources that were cited
        cited_indices = sorted(set(c.source_index for c in citations))
        
        citation_list = []
        for idx in cited_indices:
            source = source_index.get(idx)
            if source:
                citation_list.append({
                    "index": idx,
                    "title": source.title,
                    "url": source.url,
                    "times_cited": sum(1 for c in citations if c.source_index == idx)
                })
                
        return citation_list
        
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitter - in production use nltk or spacy
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Clean up sentences
        cleaned = []
        for sent in sentences:
            sent = sent.strip()
            if sent and len(sent) > 10:  # Skip very short fragments
                cleaned.append(sent)
                
        return cleaned
        
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity (0-1)"""
        # Simple implementation - in production use better similarity metrics
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        if text1_lower == text2_lower:
            return 1.0
            
        # Check if one contains the other
        if text1_lower in text2_lower or text2_lower in text1_lower:
            return 0.8
            
        # Count common words
        words1 = set(text1_lower.split())
        words2 = set(text2_lower.split())
        
        if not words1 or not words2:
            return 0.0
            
        common = len(words1.intersection(words2))
        total = len(words1.union(words2))
        
        return common / total if total > 0 else 0.0
            
    async def generate_bibliography(
        self,
        sources: List[SearchResult],
        citation_list: List[Dict[str, Any]],
        style: str = "MLA"
    ) -> str:
        """Generate a formatted bibliography"""
        
        bibliography = "\n\n## References\n\n"
        
        for citation in citation_list:
            idx = citation["index"]
            # Find the source by matching the citation info
            source = None
            for s in sources:
                if s.url == citation["url"]:
                    source = s
                    break
            
            if source:
                if style == "MLA":
                    # Simple MLA-style citation
                    entry = f"[{idx}] \"{source.title}.\" Web. {source.url}"
                elif style == "APA":
                    # Simple APA-style citation
                    entry = f"[{idx}] {source.title}. Retrieved from {source.url}"
                else:
                    # Default simple format
                    entry = f"[{idx}] {source.title}. {source.url}"
                    
                bibliography += entry + "\n\n"
                
        return bibliography