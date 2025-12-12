from __future__ import annotations

"""
Multi-Source Data Intelligence Module
Real-time web scraping, API integration, and cross-reference verification
"""

import asyncio
import json
import csv
import time
import hashlib
import re
import logging
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

try:
    from bs4 import BeautifulSoup  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    BeautifulSoup = None  # type: ignore

try:
    import pandas as pd  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    pd = None  # type: ignore

try:  # Optional dependency
    import aiohttp  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    aiohttp = None  # type: ignore


def _require_aiohttp() -> None:
    """Guard to ensure aiohttp is available before using async collectors."""
    if aiohttp is None:  # pragma: no cover - executed only when missing
        raise ModuleNotFoundError(
            "aiohttp is required for the async data collector. "
            "Install optional dependencies with `python3 -m pip install -r requirements.txt`."
        )


def _require_pandas() -> None:
    """Ensure pandas is installed before performing DataFrame operations."""
    if pd is None:  # pragma: no cover - executed only when missing
        raise ModuleNotFoundError(
            "pandas is required for structured data collection. "
            "Install optional dependencies with `python3 -m pip install -r requirements.txt`."
        )


def _require_bs4() -> None:
    """Ensure BeautifulSoup is present before parsing HTML."""
    if BeautifulSoup is None:  # pragma: no cover - executed only when missing
        raise ModuleNotFoundError(
            "beautifulsoup4 is required for HTML parsing. "
            "Install optional dependencies with `python3 -m pip install -r requirements.txt`."
        )


@dataclass
class DataSource:
    """Represents a data source configuration"""

    name: str
    url: str
    source_type: str  # 'web', 'api', 'file', 'database'
    headers: Dict[str, str] = None
    params: Dict[str, Any] = None
    auth: Dict[str, str] = None
    rate_limit: float = 1.0  # seconds between requests
    timeout: int = 30
    retry_count: int = 3


class DataCollector:
    """
    Advanced data collection system with multi-source intelligence
    """

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.session = None
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.rate_limiters = {}

    async def __aenter__(self):
        """Async context manager entry"""
        _require_aiohttp()
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=self.max_concurrent),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _get_cache_key(self, url: str, params: Dict = None) -> str:
        """Generate cache key for request"""
        key_data = f"{url}_{json.dumps(params, sort_keys=True) if params else ''}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def _rate_limit(self, source_name: str, rate_limit: float):
        """Apply rate limiting per source"""
        if source_name not in self.rate_limiters:
            self.rate_limiters[source_name] = 0

        elapsed = time.time() - self.rate_limiters[source_name]
        if elapsed < rate_limit:
            await asyncio.sleep(rate_limit - elapsed)

        self.rate_limiters[source_name] = time.time()

    async def scrape_webpage(
        self, source: DataSource, selectors: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Scrape webpage with intelligent content extraction
        """
        _require_bs4()
        await self._rate_limit(source.name, source.rate_limit)

        cache_key = self._get_cache_key(source.url, source.params)
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            headers = source.headers or {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with self.session.get(
                source.url,
                headers=headers,
                params=source.params,
                timeout=source.timeout,
            ) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Extract data based on selectors or intelligent extraction
                    extracted_data = {}

                    if selectors:
                        for key, selector in selectors.items():
                            elements = soup.select(selector)
                            extracted_data[key] = [
                                elem.get_text(strip=True) for elem in elements
                            ]
                    else:
                        # Intelligent extraction
                        extracted_data = self._intelligent_extract(soup)

                    result = {
                        "url": source.url,
                        "status": response.status,
                        "data": extracted_data,
                        "metadata": {
                            "title": soup.title.string if soup.title else "",
                            "timestamp": time.time(),
                            "content_length": len(html),
                        },
                    }

                    self.cache[cache_key] = result
                    return result
                else:
                    raise Exception(f"HTTP {response.status}: {response.reason}")

        except Exception as e:
            self.logger.error(f"Error scraping {source.url}: {e}")
            return {"url": source.url, "error": str(e), "status": "failed"}

    def _intelligent_extract(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Intelligent content extraction without predefined selectors
        """
        _require_bs4()
        data = {}

        # Extract headings
        headings = []
        for level in range(1, 7):
            for heading in soup.find_all(f"h{level}"):
                headings.append(
                    {
                        "level": level,
                        "text": heading.get_text(strip=True),
                        "id": heading.get("id", ""),
                    }
                )
        data["headings"] = headings

        # Extract paragraphs
        paragraphs = [
            p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)
        ]
        data["paragraphs"] = paragraphs

        # Extract lists
        lists = []
        for ul in soup.find_all(["ul", "ol"]):
            items = [li.get_text(strip=True) for li in ul.find_all("li")]
            lists.append({"type": ul.name, "items": items})
        data["lists"] = lists

        # Extract tables
        tables = []
        for table in soup.find_all("table"):
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                rows.append(cells)
            if rows:
                tables.append(rows)
        data["tables"] = tables

        # Extract links
        links = []
        for a in soup.find_all("a", href=True):
            links.append(
                {
                    "text": a.get_text(strip=True),
                    "href": a["href"],
                    "title": a.get("title", ""),
                }
            )
        data["links"] = links

        # Extract images
        images = []
        for img in soup.find_all("img", src=True):
            images.append(
                {
                    "src": img["src"],
                    "alt": img.get("alt", ""),
                    "title": img.get("title", ""),
                }
            )
        data["images"] = images

        return data

    async def fetch_api_data(self, source: DataSource) -> Dict[str, Any]:
        """
        Fetch data from API endpoints with authentication and error handling
        """
        await self._rate_limit(source.name, source.rate_limit)

        cache_key = self._get_cache_key(source.url, source.params)
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            headers = source.headers or {"Content-Type": "application/json"}

            # Add authentication if provided
            if source.auth:
                if "bearer" in source.auth:
                    headers["Authorization"] = f"Bearer {source.auth['bearer']}"
                elif "api_key" in source.auth:
                    headers["X-API-Key"] = source.auth["api_key"]

            async with self.session.get(
                source.url,
                headers=headers,
                params=source.params,
                timeout=source.timeout,
            ) as response:
                if response.status == 200:
                    if response.content_type == "application/json":
                        data = await response.json()
                    else:
                        data = await response.text()

                    result = {
                        "url": source.url,
                        "status": response.status,
                        "data": data,
                        "metadata": {
                            "content_type": response.content_type,
                            "timestamp": time.time(),
                            "headers": dict(response.headers),
                        },
                    }

                    self.cache[cache_key] = result
                    return result
                else:
                    raise Exception(
                        f"API Error {response.status}: {await response.text()}"
                    )

        except Exception as e:
            self.logger.error(f"Error fetching API data from {source.url}: {e}")
            return {"url": source.url, "error": str(e), "status": "failed"}

    async def batch_collect(
        self, sources: List[DataSource], selectors: Dict[str, Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect data from multiple sources simultaneously
        """
        tasks = []

        for source in sources:
            if source.source_type == "web":
                selector = selectors.get(source.name) if selectors else None
                task = self.scrape_webpage(source, selector)
            elif source.source_type == "api":
                task = self.fetch_api_data(source)
            else:
                continue

            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    {
                        "source": sources[i].name,
                        "error": str(result),
                        "status": "failed",
                    }
                )
            else:
                processed_results.append(result)

        return processed_results

    def cross_reference_verify(
        self, data_sets: List[Dict[str, Any]], verification_fields: List[str]
    ) -> Dict[str, Any]:
        """
        Cross-reference verification across different data sources
        """
        verification_results = {
            "verified_data": {},
            "conflicts": {},
            "confidence_scores": {},
            "source_reliability": {},
        }

        # Extract verification fields from each dataset
        field_data = {}
        for field in verification_fields:
            field_data[field] = {}

            for dataset in data_sets:
                source_name = dataset.get("metadata", {}).get("source", "unknown")
                if "data" in dataset and field in dataset["data"]:
                    field_data[field][source_name] = dataset["data"][field]

        # Perform cross-reference verification
        for field, sources in field_data.items():
            if len(sources) < 2:
                continue

            # Find consensus
            values = list(sources.values())
            unique_values = list(set(str(v) for v in values))

            if len(unique_values) == 1:
                # All sources agree
                verification_results["verified_data"][field] = values[0]
                verification_results["confidence_scores"][field] = 1.0
            else:
                # Conflict detected
                verification_results["conflicts"][field] = sources

                # Calculate confidence based on source agreement
                value_counts = {}
                for value in values:
                    str_val = str(value)
                    value_counts[str_val] = value_counts.get(str_val, 0) + 1

                # Most common value wins
                most_common = max(value_counts.items(), key=lambda x: x[1])
                verification_results["verified_data"][field] = most_common[0]
                verification_results["confidence_scores"][field] = most_common[1] / len(
                    values
                )

        return verification_results

    def clean_and_transform(
        self, raw_data: List[Dict[str, Any]], transformations: Dict[str, Any] = None
    ) -> "pd.DataFrame":
        """
        Automated data cleaning and transformation pipeline
        """
        _require_pandas()
        # Convert to DataFrame for easier manipulation
        all_data = []

        for dataset in raw_data:
            if "data" in dataset and isinstance(dataset["data"], dict):
                flattened = self._flatten_dict(dataset["data"])
                flattened["_source"] = dataset.get("url", "unknown")
                flattened["_timestamp"] = dataset.get("metadata", {}).get(
                    "timestamp", time.time()
                )
                all_data.append(flattened)

        if not all_data:
            return pd.DataFrame()

        df = pd.DataFrame(all_data)

        # Apply transformations if provided
        if transformations:
            df = self._apply_transformations(df, transformations)

        # Basic cleaning
        df = self._basic_cleaning(df)

        return df

    def _flatten_dict(self, d: Dict, parent_key: str = "", sep: str = "_") -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                # Handle list of dictionaries
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(
                            self._flatten_dict(item, f"{new_key}_{i}", sep=sep).items()
                        )
            else:
                items.append((new_key, v))
        return dict(items)

    def _apply_transformations(
        self, df: "pd.DataFrame", transformations: Dict[str, Any]
    ) -> "pd.DataFrame":
        """Apply custom transformations to DataFrame"""
        _require_pandas()
        for column, transform in transformations.items():
            if column in df.columns:
                if transform["type"] == "numeric":
                    df[column] = pd.to_numeric(df[column], errors="coerce")
                elif transform["type"] == "datetime":
                    df[column] = pd.to_datetime(df[column], errors="coerce")
                elif transform["type"] == "categorical":
                    df[column] = df[column].astype("category")
                elif transform["type"] == "regex_extract":
                    pattern = transform["pattern"]
                    df[column] = df[column].str.extract(pattern, expand=False)

        return df

    def _basic_cleaning(self, df: "pd.DataFrame") -> "pd.DataFrame":
        """Apply basic data cleaning operations"""
        _require_pandas()
        # Remove completely empty rows
        df = df.dropna(how="all")

        # Clean string columns
        string_columns = df.select_dtypes(include=["object"]).columns
        for col in string_columns:
            if col in df.columns:
                # Strip whitespace
                df[col] = df[col].astype(str).str.strip()
                # Replace empty strings with NaN
                df[col] = df[col].replace("", pd.NA)

        return df

    def export_data(
        self, df: "pd.DataFrame", file_path: str, format: str = "csv"
    ) -> bool:
        """Export cleaned data to various formats"""
        _require_pandas()
        try:
            if format.lower() == "csv":
                df.to_csv(file_path, index=False)
            elif format.lower() == "json":
                df.to_json(file_path, orient="records", indent=2)
            elif format.lower() == "excel":
                df.to_excel(file_path, index=False)
            elif format.lower() == "parquet":
                df.to_parquet(file_path, index=False)
            else:
                raise ValueError(f"Unsupported format: {format}")

            self.logger.info(f"Data exported to {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            return False


# Synchronous wrapper for easier integration
class SyncDataCollector:
    """Synchronous wrapper for DataCollector"""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.logger = logging.getLogger(__name__)

    def collect_data(
        self, sources: List[DataSource], selectors: Dict[str, Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """Synchronous data collection"""

        async def _collect():
            async with DataCollector(self.max_concurrent) as collector:
                return await collector.batch_collect(sources, selectors)

        return asyncio.run(_collect())

    def scrape_single_page(
        self, url: str, selectors: Dict[str, str] = None, headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Scrape a single webpage synchronously"""
        source = DataSource(
            name="single_page", url=url, source_type="web", headers=headers
        )

        async def _scrape():
            async with DataCollector(1) as collector:
                return await collector.scrape_webpage(source, selectors)

        return asyncio.run(_scrape())


# Example usage
if __name__ == "__main__":
    # Example data sources
    sources = [
        DataSource(
            name="news_site",
            url="https://example-news.com",
            source_type="web",
            rate_limit=2.0,
        ),
        DataSource(
            name="api_endpoint",
            url="https://api.example.com/data",
            source_type="api",
            headers={"Accept": "application/json"},
            auth={"api_key": "your_api_key"},
        ),
    ]

    # Synchronous usage
    collector = SyncDataCollector()
    results = collector.collect_data(sources)
    print(f"Collected {len(results)} datasets")
