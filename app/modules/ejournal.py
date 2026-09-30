import asyncio
import re
from typing import Any

from lxml import html
from fastapi import APIRouter, HTTPException, status
from scrapling.fetchers import Fetcher
from scrapling.parser import Adaptor

from app.config import settings
from app.envelope import success_response, error_response
from app.cache import cache
from app.router_helper import cached_endpoint
from app.proxy import get_proxy

router = APIRouter(prefix="/v1/ejournal", tags=["ejournal"])

def parse_journal_catalog(html_str: str) -> list[dict[str, Any]]:
    tree = html.fromstring(html_str)
    h3_nodes = tree.xpath("//h3")

    journals = []
    seen_slugs = set()

    if h3_nodes:
        content = h3_nodes[0].getparent()
        current_title = None

        for elem in content:
            if elem.tag == "h3":
                current_title = elem.text_content().strip()
            elif current_title:
                for a in elem.xpath(".//a/@href"):
                    m = re.search(r"(?:ejournal\.bsi\.ac\.id|jurnal\.bsi\.ac\.id)/(?:ejurnal/)?(?:index\.php/)?([a-zA-Z0-9_\-]+)/?$", a)
                    if m:
                        slug = m.group(1).lower()
                        if slug not in ("index", "user", "about", "search", "login", "register", "help") and slug not in seen_slugs:
                            seen_slugs.add(slug)
                            journals.append({
                                "name": current_title,
                                "slug": slug,
                                "url": a if a.startswith("http") else f"https://ejournal.bsi.ac.id{a}",
                            })
                            current_title = None
                            break

    # Fallback for simple link lists or fixture HTML
    if not journals:
        page = Adaptor(html_str)
        for a in page.css('a[href*="/ejurnal/index.php/"]'):
            href = a.attrib.get("href", "").strip()
            title = " ".join(a.text.split()).strip()
            m = re.search(r"/ejurnal/index.php/([^/#\?]+)/?", href)
            if m:
                slug = m.group(1).lower()
                if slug not in seen_slugs and slug not in ("index", "about", "search"):
                    seen_slugs.add(slug)
                    display_name = title if title and len(title) > 2 else f"Jurnal {slug.capitalize()}"
                    journals.append({
                        "name": display_name,
                        "slug": slug,
                        "url": href if href.startswith("http") else f"https://ejournal.bsi.ac.id{href}",
                    })

    return journals

class EJournalClient:
    BASE_URL = "https://ejournal.bsi.ac.id"

    def fetch_catalog(self) -> str:
        # Bypasses Cloudflare challenge via OAI identifier fallback
        url = f"{self.BASE_URL}/ejurnal/oai?verb=Identify"
        try:
            res = Fetcher.get(url, timeout=30, impersonate="chrome", proxy=get_proxy())
            if res.status == 200:
                body = res.body if isinstance(res.body, bytes) else str(res.body).encode("utf-8")
                return body.decode("utf-8", "ignore")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message=f"Status {res.status}", module="ejournal")
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="ejournal")
            )

ejournal_client = EJournalClient()

@router.get("/journals")
async def get_journals():
    loop = asyncio.get_running_loop()
    return await cached_endpoint(
        module="ejournal",
        name="catalog",
        fetch=lambda: loop.run_in_executor(None, ejournal_client.fetch_catalog),
        parse=parse_journal_catalog,
        ttl=settings.TTL_LIBRARY,
    )
