"""
Orchestrator for Stock Mini-App Prompt Flow

Coordinates multiple microservices to execute the complete prompt analysis workflow.
This is application-specific logic, not a reusable module.
"""

import uuid
import logging
import os
from typing import Dict, Any, Optional
import httpx
from datetime import datetime

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

if DEBUG_MODE or ENVIRONMENT == "development":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] [run_id=%(run_id)s] %(name)s: %(message)s'
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )


class PromptOrchestrator:
    """
    Orchestrates the complete prompt flow for stock analysis.
    
    Coordinates calls to:
    - data-store: Company data retrieval and prompt storage
    - prompt-manager: Template loading and filling
    - prompt-security: Prompt validation (optional)
    - llm-provider: Response generation
    - format-converter: HTML/MD/JSON rendering
    """
    
    def __init__(self):
        self.data_store_url = os.getenv("DATA_STORE_URL", "http://localhost:8007")
        self.prompt_manager_url = os.getenv("PROMPT_MANAGER_URL", "http://localhost:8000")
        self.llm_provider_url = os.getenv("LLM_PROVIDER_URL", "http://localhost:8001")
        self.format_converter_url = os.getenv("FORMAT_CONVERTER_URL", "http://localhost:8004")
        self.prompt_security_url = os.getenv("PROMPT_SECURITY_URL", "http://localhost:8002")
        
        # HTTP client with timeout
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def run_prompt_flow(self, ticker: str) -> Dict[str, Any]:
        """
        Orchestrate the complete prompt flow for a ticker.
        
        Steps:
        1. Fetch company data from data-store
        2. Load context files via prompt-manager
        3. Fill prompt template with ticker + company data
        4. Validate/sanitize prompt (if security module available)
        5. Generate LLM response (mock mode)
        6. Store prompt + response in data-store
        7. Convert response to HTML/MD/JSON via format-converter
        8. Update stored response with rendered formats
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
            
        Returns:
            Dict with run_id, ticker, html_url, md_url, json_url, status
        """
        run_id = str(uuid.uuid4())
        log_extra = {"run_id": run_id}
        
        try:
            logger.info(f"Starting prompt flow for ticker: {ticker}", extra=log_extra)
            
            # Step 1: Fetch company data
            logger.info(f"Step 1: Fetching company data", extra=log_extra)
            company_data = await self._fetch_company_data(ticker, run_id)
            
            # Step 2: Load context files
            logger.info(f"Step 2: Loading context files", extra=log_extra)
            contexts = await self._load_contexts(run_id)
            
            # Step 3: Fill prompt template
            logger.info(f"Step 3: Filling prompt template", extra=log_extra)
            filled_prompt = await self._fill_prompt(ticker, company_data, contexts, run_id)
            
            # Step 4: Validate prompt (optional)
            logger.info(f"Step 4: Validating prompt", extra=log_extra)
            sanitized_prompt = await self._validate_prompt(filled_prompt, run_id)
            
            # Step 5: Generate LLM response
            logger.info(f"Step 5: Generating LLM response", extra=log_extra)
            llm_response = await self._generate_response(sanitized_prompt, ticker, run_id)
            
            # Step 6: Convert to HTML/MD/JSON (before storing)
            logger.info(f"Step 6: Rendering formats", extra=log_extra)
            rendered_formats = await self._render_formats(llm_response, run_id)
            
            # Step 7: Store in data-store (with rendered formats)
            logger.info(f"Step 7: Storing prompt run", extra=log_extra)
            stored_key = await self._store_prompt_run(
                run_id, ticker, sanitized_prompt, llm_response, company_data, rendered_formats, run_id
            )
            
            logger.info(f"Prompt flow completed successfully", extra=log_extra)
            
            return {
                "success": True,
                "run_id": run_id,
                "ticker": ticker,
                "html_url": f"/api/prompt/run/{run_id}/html",
                "md_url": f"/api/prompt/run/{run_id}/md",
                "json_url": f"/api/prompt/run/{run_id}/json",
                "status": "completed"
            }
        except httpx.ConnectError as e:
            logger.error(
                f"Connection error in prompt flow: {str(e)}",
                extra=log_extra,
                exc_info=DEBUG_MODE
            )
            return {
                "success": False,
                "run_id": run_id,
                "ticker": ticker,
                "error": f"Connection error: {str(e)}",
                "status": "failed"
            }
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error in prompt flow: {e.response.status_code} - {e.response.text[:200]}",
                extra=log_extra,
                exc_info=DEBUG_MODE
            )
            return {
                "success": False,
                "run_id": run_id,
                "ticker": ticker,
                "error": f"HTTP {e.response.status_code}: {e.response.text[:200]}",
                "status": "failed"
            }
        except Exception as e:
            logger.error(
                f"Prompt flow failed: {type(e).__name__}: {str(e)}",
                extra=log_extra,
                exc_info=DEBUG_MODE
            )
            return {
                "success": False,
                "run_id": run_id,
                "ticker": ticker,
                "error": f"{type(e).__name__}: {str(e)}",
                "status": "failed"
            }
    
    async def _fetch_company_data(self, ticker: str, run_id: str) -> Dict[str, Any]:
        """
        Fetch company data from data-store.
        
        Calls data-store API to retrieve company financial data from MongoDB seed_companies collection.
        Returns company data structure with valuation, financials, profitability fields.
        """
        log_extra = {"run_id": run_id}
        
        try:
            # Query for company by ticker
            # Note: MongoDB store searches both metadata.ticker and data.ticker automatically
            url = f"{self.data_store_url}/query"
            logger.debug(f"Calling data-store: {url}", extra=log_extra)
            response = await self.client.post(
                url,
                json={
                    "collection": "seed_companies",
                    "filters": {"ticker": ticker.upper()},  # Store searches both metadata.ticker and data.ticker
                    "sort": {"stored_at": -1},  # Get latest
                    "limit": 1
                }
            )
            logger.debug(f"data-store response: {response.status_code}", extra=log_extra)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("items", [])
            
            if not items:
                raise ValueError(f"Company data not found for ticker: {ticker}")
            
            company_data = items[0].get("data", {})
            logger.debug(f"Fetched company data for {ticker}", extra=log_extra)
            return company_data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching company data: {e}", extra=log_extra)
            raise
        except Exception as e:
            logger.error(f"Error fetching company data: {e}", extra=log_extra, exc_info=DEBUG_MODE)
            raise
    
    async def _load_contexts(self, run_id: str) -> str:
        """
        Load context files via prompt-manager.
        
        Calls prompt-manager API to load markdown context files from disk (e.g., biotech/01-introduction.md).
        Merges multiple context files into a single string for prompt composition.
        """
        log_extra = {"run_id": run_id}
        
        try:
            # Load default context files
            context_paths = [
                "biotech/01-introduction.md",
                "economical-context.md"
            ]
            
            url = f"{self.prompt_manager_url}/prompt/load-contexts"
            logger.debug(f"Calling prompt-manager: {url}", extra=log_extra)
            response = await self.client.post(
                url,
                json={"context_paths": context_paths}
            )
            logger.debug(f"prompt-manager response: {response.status_code}", extra=log_extra)
            response.raise_for_status()
            
            data = response.json()
            contexts = data.get("content", "")
            logger.debug(f"Loaded {len(context_paths)} context files", extra=log_extra)
            return contexts
            
        except httpx.HTTPStatusError as e:
            logger.warning(f"Failed to load contexts, using empty: {e}", extra=log_extra)
            return ""  # Graceful degradation
        except Exception as e:
            logger.warning(f"Error loading contexts: {e}", extra=log_extra, exc_info=DEBUG_MODE)
            return ""  # Graceful degradation
    
    async def _fill_prompt(self, ticker: str, company_data: Dict[str, Any], 
                          contexts: str, run_id: str) -> str:
        """
        Fill prompt template with ticker, company_data, and contexts.
        
        Calls prompt-manager API to fill template variables with ticker, company_data, and contexts.
        Returns a complete prompt string ready for LLM processing.
        """
        log_extra = {"run_id": run_id}
        
        try:
            # Create a simple prompt template for stock analysis
            template_content = """Analyze the following stock:

Ticker: {ticker}

Company Data:
{company_data}

Context:
{context}

Provide a comprehensive analysis including:
1. Valuation assessment
2. Financial health
3. Growth prospects
4. Risk factors
5. Investment recommendation
"""
            
            # Format company data as JSON string for prompt
            import json
            company_data_str = json.dumps(company_data, indent=2)
            
            url = f"{self.prompt_manager_url}/prompt/fill"
            logger.debug(f"Calling prompt-manager fill: {url}", extra=log_extra)
            response = await self.client.post(
                url,
                json={
                    "template_content": template_content,
                    "params": {
                        "ticker": ticker,
                        "company_data": company_data_str,
                        "context": contexts
                    }
                }
            )
            logger.debug(f"prompt-manager fill response: {response.status_code}", extra=log_extra)
            response.raise_for_status()
            
            data = response.json()
            filled_prompt = data.get("content", "")
            logger.debug(f"Filled prompt template ({len(filled_prompt)} chars)", extra=log_extra)
            return filled_prompt
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error filling prompt: {e}", extra=log_extra)
            raise
        except Exception as e:
            logger.error(f"Error filling prompt: {e}", extra=log_extra, exc_info=DEBUG_MODE)
            raise
    
    async def _validate_prompt(self, filled_prompt: str, run_id: str) -> str:
        """
        Validate and sanitize prompt (optional).
        
        Calls prompt-security API to validate and sanitize the filled prompt for injection attacks.
        Returns sanitized prompt string, or original if security module unavailable (graceful degradation).
        """
        log_extra = {"run_id": run_id}
        
        try:
            response = await self.client.post(
                f"{self.prompt_security_url}/validate",
                json={"prompt": filled_prompt},
                timeout=10.0
            )
            response.raise_for_status()
            
            data = response.json()
            sanitized = data.get("sanitized_prompt", filled_prompt)
            logger.debug(f"Prompt validated and sanitized", extra=log_extra)
            return sanitized
            
        except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException):
            # Graceful degradation - security module is optional
            logger.info(f"Prompt security not available, using original prompt", extra=log_extra)
            return filled_prompt
        except Exception as e:
            logger.warning(f"Error validating prompt: {e}, using original", extra=log_extra, exc_info=DEBUG_MODE)
            return filled_prompt
    
    async def _generate_response(self, sanitized_prompt: str, ticker: str, run_id: str) -> Dict[str, Any]:
        """
        Generate LLM response.
        
        Calls llm-provider REST API (port 8001) to generate response from sanitized prompt.
        Supports provider swapping via request parameters (use_mock=true for v1).
        Returns response with content, tokens_used, model, cost, and metadata.
        """
        log_extra = {"run_id": run_id}
        
        try:
            url = f"{self.llm_provider_url}/generate"
            logger.debug(f"Calling llm-provider: {url}", extra=log_extra)
            response = await self.client.post(
                url,
                json={
                    "prompt": sanitized_prompt,
                    "use_mock": True,  # v1: use mock provider
                    "ticker": ticker  # Context for mock provider
                }
            )
            logger.debug(f"llm-provider response: {response.status_code}", extra=log_extra)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Generated LLM response ({data.get('tokens_used', 0)} tokens)", extra=log_extra)
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error generating response: {e}", extra=log_extra)
            raise
        except Exception as e:
            logger.error(f"Error generating response: {e}", extra=log_extra, exc_info=DEBUG_MODE)
            raise
    
    async def _store_prompt_run(self, run_id: str, ticker: str, sanitized_prompt: str,
                                llm_response: Dict[str, Any], company_data: Dict[str, Any],
                                rendered_formats: Dict[str, str], run_id_log: str) -> str:
        """
        Store prompt run in data-store.
        
        Calls data-store API to persist prompt run in MongoDB prompt_runs collection.
        Stores run_id, ticker, prompt, raw LLM response, and metadata; returns stored key.
        """
        log_extra = {"run_id": run_id_log}
        
        try:
            # Create document structure
            document = {
                "run_id": run_id,
                "ticker": ticker.upper(),
                "prompt_template": "",  # Could store template path if needed
                "filled_prompt": sanitized_prompt,
                "sanitized_prompt": sanitized_prompt,
                "llm_response_raw": llm_response.get("content", ""),
                "llm_response_html": rendered_formats.get("html", ""),
                "llm_response_md": rendered_formats.get("md", ""),
                "llm_response_json": rendered_formats.get("json", {}),
                "company_data": company_data,  # Snapshot of company data used
                "metadata": {
                    "model_used": llm_response.get("model", "mock"),
                    "provider": llm_response.get("provider", "mock"),
                    "tokens_used": llm_response.get("tokens_used", 0),
                    "cost": llm_response.get("cost", 0.0),
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "completed"
                }
            }
            
            key = f"prompt_run:{run_id}"
            
            response = await self.client.post(
                f"{self.data_store_url}/store",
                json={
                    "key": key,
                    "data": document,
                    "collection": "prompt_runs"
                }
            )
            response.raise_for_status()
            
            logger.debug(f"Stored prompt run with key: {key}", extra=log_extra)
            return key
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error storing prompt run: {e}", extra=log_extra)
            raise
        except Exception as e:
            logger.error(f"Error storing prompt run: {e}", extra=log_extra, exc_info=DEBUG_MODE)
            raise
    
    async def _render_formats(self, llm_response: Dict[str, Any], run_id: str) -> Dict[str, str]:
        """
        Convert LLM response to HTML/MD/JSON.
        
        Calls format-converter API to render LLM response (markdown) into HTML, MD, and JSON formats.
        Returns dictionary with html, md, and json keys containing rendered content.
        """
        log_extra = {"run_id": run_id}
        
        try:
            content = llm_response.get("content", "")
            
            # Convert to HTML
            url = f"{self.format_converter_url}/convert"
            logger.debug(f"Calling format-converter (HTML): {url}", extra=log_extra)
            html_response = await self.client.post(
                url,
                json={
                    "content": content,
                    "source_format": "markdown",
                    "target_format": "html"
                }
            )
            logger.debug(f"format-converter (HTML) response: {html_response.status_code}", extra=log_extra)
            html_response.raise_for_status()
            html_data = html_response.json()
            html = html_data.get("content", "")
            
            # MD is already the source, just return it
            md = content
            
            # Convert to JSON (structured format)
            logger.debug(f"Calling format-converter (JSON): {url}", extra=log_extra)
            json_response = await self.client.post(
                url,
                json={
                    "content": content,
                    "source_format": "markdown",
                    "target_format": "json"
                }
            )
            logger.debug(f"format-converter (JSON) response: {json_response.status_code}", extra=log_extra)
            json_response.raise_for_status()
            json_data = json_response.json()
            json_content = json_data.get("content", {})
            
            rendered = {
                "html": html,
                "md": md,
                "json": json_content if isinstance(json_content, dict) else {"content": json_content}
            }
            
            logger.debug(f"Rendered formats: HTML ({len(html)} chars), MD ({len(md)} chars)", extra=log_extra)
            return rendered
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error rendering formats: {e}", extra=log_extra)
            # Return empty formats on error
            return {"html": "", "md": llm_response.get("content", ""), "json": {}}
        except Exception as e:
            logger.error(f"Error rendering formats: {e}", extra=log_extra, exc_info=DEBUG_MODE)
            return {"html": "", "md": llm_response.get("content", ""), "json": {}}
    

