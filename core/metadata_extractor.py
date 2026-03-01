"""
Extracción de metadatos académicos desde múltiples fuentes:
- DOI → CrossRef + OpenAlex
- arXiv → arXiv API (XML)
- GitHub → GitHub REST API
- PDF remoto → descarga temporal + PyMuPDF
- Web genérica → scraping de título y meta description

Diseñado para ser resiliente: retry con backoff, timeouts, y fallback entre APIs.
"""

import logging
import re
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from config.settings import (
    API_BACKOFF_FACTOR,
    API_MAX_RETRIES,
    API_TIMEOUT,
    CROSSREF_BASE_URL,
    CROSSREF_MAILTO,
    OPENALEX_BASE_URL,
    OPENALEX_MAILTO,
)

logger = logging.getLogger("bibliografias")

_USER_AGENT = (
    "BibliografiasBot/1.0 (Academic bibliography tracker; "
    "mailto:researcher@example.com)"
)


# ============================================================
# Detección del tipo de URL
# ============================================================

def _classify_url(url: str) -> str:
    """Clasifica una URL en: doi, arxiv, github, pdf, web."""
    url_lower = url.strip().lower()

    if extract_doi(url) is not None:
        return "doi"

    if "arxiv.org" in url_lower:
        return "arxiv"

    if "github.com" in url_lower:
        return "github"

    if url_lower.endswith(".pdf"):
        return "pdf"

    return "web"


# ============================================================
# Utilidades comunes
# ============================================================

def extract_doi(url_or_doi: str) -> str | None:
    """Extrae un DOI limpio de una URL o string directo."""
    url_or_doi = url_or_doi.strip()
    match = re.search(r"(10\.\d{4,9}/[^\s]+)", url_or_doi)
    if match:
        return match.group(1).rstrip(".")
    return None


def _request_with_retry(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
) -> requests.Response | None:
    """Realiza GET con retry + backoff exponencial. Retorna Response crudo."""
    default_headers = {"User-Agent": _USER_AGENT}
    if headers:
        default_headers.update(headers)

    for attempt in range(1, API_MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url, params=params, headers=default_headers, timeout=API_TIMEOUT
            )
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 0
            if status == 404:
                logger.warning("Recurso no encontrado (404): %s", url)
                return None
            logger.warning(
                "HTTP %d en intento %d/%d: %s",
                status, attempt, API_MAX_RETRIES, url,
            )
        except requests.exceptions.RequestException as e:
            logger.warning(
                "Error de red en intento %d/%d: %s — %s",
                attempt, API_MAX_RETRIES, url, e,
            )
        if attempt < API_MAX_RETRIES:
            wait = API_BACKOFF_FACTOR ** attempt
            logger.info("Esperando %ds antes de reintentar...", wait)
            time.sleep(wait)
    return None


def _get_json(url: str, params: dict | None = None) -> dict | None:
    """Wrapper para obtener JSON con retry."""
    resp = _request_with_retry(url, params=params)
    if resp is None:
        return None
    try:
        data = resp.json()
        resp.close()
        return data
    except Exception:
        resp.close()
        return None


def _strip_html(text: str) -> str:
    """Elimina etiquetas HTML/JATS simples."""
    return re.sub(r"<[^>]+>", "", text).strip()


# ============================================================
# Extractor: CrossRef (DOI)
# ============================================================

def _extract_crossref(doi: str) -> dict[str, Any] | None:
    """Extrae metadatos de un DOI usando la API de CrossRef."""
    url = f"{CROSSREF_BASE_URL}/{doi}"
    params = {}
    if CROSSREF_MAILTO:
        params["mailto"] = CROSSREF_MAILTO

    data = _get_json(url, params)
    if not data or "message" not in data:
        return None

    msg = data["message"]

    authors_raw = msg.get("author", [])
    authors = [
        f"{a.get('family', '')}, {a.get('given', '')}".strip(", ")
        for a in authors_raw
    ]

    date_parts = msg.get("published-print", msg.get("published-online", {}))
    year = ""
    if date_parts and "date-parts" in date_parts:
        parts = date_parts["date-parts"]
        if parts and parts[0]:
            year = str(parts[0][0])

    container = msg.get("container-title", [])
    journal = container[0] if container else ""

    title_list = msg.get("title", [])
    title = title_list[0] if title_list else ""

    abstract_raw = msg.get("abstract", "")
    abstract = _strip_html(abstract_raw)

    return {
        "titulo": title,
        "autores": authors,
        "anio": year,
        "journal": journal,
        "doi": doi,
        "abstract": abstract,
        "tipo": msg.get("type", ""),
        "url": msg.get("URL", ""),
        "fuente_metadata": "CrossRef",
    }


# ============================================================
# Extractor: OpenAlex (DOI)
# ============================================================

def _extract_openalex(doi: str) -> dict[str, Any] | None:
    """Extrae metadatos usando OpenAlex."""
    url = f"{OPENALEX_BASE_URL}/doi:{doi}"
    params = {}
    if OPENALEX_MAILTO:
        params["mailto"] = OPENALEX_MAILTO

    data = _get_json(url, params)
    if not data or "id" not in data:
        return None

    authorships = data.get("authorships", [])
    authors = [
        a.get("author", {}).get("display_name", "")
        for a in authorships
        if a.get("author", {}).get("display_name")
    ]

    year = str(data.get("publication_year", ""))

    locations = data.get("locations", [])
    journal = ""
    for loc in locations:
        source = loc.get("source")
        if source and source.get("display_name"):
            journal = source["display_name"]
            break

    abstract = _rebuild_openalex_abstract(
        data.get("abstract_inverted_index")
    )

    return {
        "titulo": data.get("display_name", ""),
        "autores": authors,
        "anio": year,
        "journal": journal,
        "doi": doi,
        "abstract": abstract,
        "tipo": data.get("type", ""),
        "url": data.get("doi", ""),
        "fuente_metadata": "OpenAlex",
    }


def _rebuild_openalex_abstract(
    inverted_index: dict[str, list[int]] | None,
) -> str:
    """Reconstruye el abstract a partir del formato inverted_index de OpenAlex."""
    if not inverted_index:
        return ""
    word_positions: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort(key=lambda x: x[0])
    return " ".join(w for _, w in word_positions)


# ============================================================
# Extractor: arXiv API
# ============================================================

def _extract_arxiv_id(url: str) -> str | None:
    """Extrae el ID de arXiv de una URL (ej: 2405.11619)."""
    match = re.search(r"arxiv\.org/abs/(\d+\.\d+)", url, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"arxiv\.org/pdf/(\d+\.\d+)", url, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _extract_arxiv(url: str) -> dict[str, Any] | None:
    """Extrae metadatos de un paper de arXiv usando su API Atom/XML."""
    arxiv_id = _extract_arxiv_id(url)
    if not arxiv_id:
        logger.warning("No se pudo extraer ID de arXiv de: %s", url)
        return None

    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    logger.info("Consultando arXiv API para ID: %s", arxiv_id)

    resp = _request_with_retry(api_url)
    if resp is None:
        return None

    try:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(resp.text)
        resp.close()

        entry = root.find("atom:entry", ns)
        if entry is None:
            return None

        title_el = entry.find("atom:title", ns)
        title = title_el.text.strip().replace("\n", " ") if title_el is not None else ""

        summary_el = entry.find("atom:summary", ns)
        abstract = summary_el.text.strip().replace("\n", " ") if summary_el is not None else ""

        authors = []
        for author_el in entry.findall("atom:author", ns):
            name_el = author_el.find("atom:name", ns)
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())

        published_el = entry.find("atom:published", ns)
        year = ""
        if published_el is not None and published_el.text:
            year = published_el.text[:4]

        # Buscar categorías
        categories = []
        for cat_el in entry.findall("atom:category", ns):
            term = cat_el.get("term", "")
            if term:
                categories.append(term)

        return {
            "titulo": title,
            "autores": authors,
            "anio": year,
            "journal": f"arXiv preprint arXiv:{arxiv_id}",
            "doi": f"10.48550/arXiv.{arxiv_id}",
            "abstract": abstract,
            "tipo": "preprint",
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "fuente_metadata": "arXiv API",
        }
    except ET.ParseError as e:
        logger.error("Error parseando XML de arXiv: %s", e)
        resp.close()
        return None


# ============================================================
# Extractor: GitHub API
# ============================================================

def _extract_github_repo(url: str) -> tuple[str, str] | None:
    """Extrae owner/repo de una URL de GitHub."""
    match = re.search(r"github\.com/([^/]+)/([^/\s?#]+)", url, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2)
    return None


def _extract_github(url: str) -> dict[str, Any] | None:
    """Extrae metadatos de un repositorio GitHub usando su API REST."""
    parts = _extract_github_repo(url)
    if not parts:
        logger.warning("No se pudo extraer owner/repo de: %s", url)
        return None

    owner, repo = parts
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    logger.info("Consultando GitHub API: %s/%s", owner, repo)

    data = _get_json(api_url)
    if not data or "id" not in data:
        return None

    description = data.get("description", "") or ""
    topics = data.get("topics", [])
    language = data.get("language", "")

    # Intentar obtener README como abstract
    readme_text = _get_github_readme(owner, repo)

    abstract_parts = []
    if description:
        abstract_parts.append(description)
    if topics:
        abstract_parts.append(f"Topics: {', '.join(topics)}")
    if language:
        abstract_parts.append(f"Lenguaje principal: {language}")
    if readme_text:
        abstract_parts.append(f"README (extracto): {readme_text[:500]}")

    created = data.get("created_at", "")
    year = created[:4] if created else ""

    owner_name = data.get("owner", {}).get("login", owner)

    return {
        "titulo": data.get("full_name", f"{owner}/{repo}"),
        "autores": [owner_name],
        "anio": year,
        "journal": "GitHub Repository",
        "doi": "",
        "abstract": "\n".join(abstract_parts),
        "tipo": "software/repository",
        "url": data.get("html_url", url),
        "fuente_metadata": "GitHub API",
    }


def _get_github_readme(owner: str, repo: str) -> str:
    """Obtiene el contenido del README de un repo GitHub (texto plano)."""
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    resp = _request_with_retry(url, headers={"Accept": "application/vnd.github.raw+json"})
    if resp is None:
        return ""
    try:
        text = resp.text[:1000]
        resp.close()
        return _strip_html(text).replace("\n", " ").strip()
    except Exception:
        return ""


# ============================================================
# Extractor: Página web genérica (scraping ligero)
# ============================================================

def _extract_web(url: str) -> dict[str, Any] | None:
    """Extrae título y descripción de una página web genérica."""
    logger.info("Scraping web para: %s", url)

    resp = _request_with_retry(url)
    if resp is None:
        return None

    try:
        html = resp.text[:10000]
        resp.close()
    except Exception:
        return None

    title = ""
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = _strip_html(title_match.group(1)).strip()

    description = ""
    desc_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        html,
        re.IGNORECASE,
    )
    if desc_match:
        description = _strip_html(desc_match.group(1)).strip()

    # Intentar el formato inverso: content antes que name
    if not description:
        desc_match = re.search(
            r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']',
            html,
            re.IGNORECASE,
        )
        if desc_match:
            description = _strip_html(desc_match.group(1)).strip()

    parsed = urlparse(url)
    domain = parsed.netloc

    return {
        "titulo": title or domain,
        "autores": [domain],
        "anio": "",
        "journal": f"Sitio web: {domain}",
        "doi": "",
        "abstract": description or f"Recurso web: {url}",
        "tipo": "webpage",
        "url": url,
        "fuente_metadata": "Web scraping",
    }


# ============================================================
# Extractor: PDF remoto
# ============================================================

def _extract_remote_pdf(url: str) -> dict[str, Any] | None:
    """Descarga un PDF remoto a archivo temporal y extrae metadatos básicos."""
    logger.info("Descargando PDF remoto: %s", url)

    try:
        resp = requests.get(
            url,
            timeout=30,
            headers={"User-Agent": _USER_AGENT},
            stream=True,
        )
        resp.raise_for_status()

        # Limitar descarga a 5 MB
        max_bytes = 5 * 1024 * 1024
        content = b""
        for chunk in resp.iter_content(chunk_size=8192):
            content += chunk
            if len(content) > max_bytes:
                logger.warning("PDF excede 5 MB, truncando descarga")
                break
        resp.close()

        import fitz  # PyMuPDF — importación tardía para no cargar si no se usa

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        doc = fitz.open(tmp_path)
        title = doc.metadata.get("title", "") or ""
        author = doc.metadata.get("author", "") or ""

        # Extraer texto de las 2 primeras páginas
        text = ""
        for page_num in range(min(2, len(doc))):
            text += doc[page_num].get_text("text") + "\n"
        doc.close()

        Path(tmp_path).unlink(missing_ok=True)

        # Intentar encontrar el abstract en el texto
        abstract = _find_abstract_in_text(text)

        # Extraer año del nombre del archivo o del texto
        year = ""
        year_match = re.search(r"20[12]\d", url)
        if year_match:
            year = year_match.group(0)

        parsed = urlparse(url)
        filename = Path(parsed.path).stem

        return {
            "titulo": title if title else filename,
            "autores": [a.strip() for a in author.split(",")] if author else [parsed.netloc],
            "anio": year,
            "journal": f"Reporte/PDF: {parsed.netloc}",
            "doi": "",
            "abstract": abstract if abstract else text[:800].strip(),
            "tipo": "report",
            "url": url,
            "fuente_metadata": "PDF remoto",
        }

    except Exception as e:
        logger.error("Error descargando/procesando PDF remoto: %s", e)
        return None


def _find_abstract_in_text(text: str) -> str:
    """Busca sección de abstract en texto extraído de PDF."""
    abstract_start = re.search(
        r"\b(abstract|resumen|summary|executive\s+summary)\b",
        text,
        re.IGNORECASE,
    )
    if not abstract_start:
        return ""

    after = text[abstract_start.end():]
    after = re.sub(r"^[\s:\-—]+", "", after)

    end_match = re.search(
        r"\b(keywords?|introduction|1\.\s|table\s+of\s+contents)\b",
        after,
        re.IGNORECASE,
    )
    if end_match:
        abstract = after[:end_match.start()]
    else:
        abstract = after[:600]

    return re.sub(r"\n(?!\n)", " ", abstract).strip()


# ============================================================
# Punto de entrada principal
# ============================================================

def extract_metadata(
    url_or_doi: str, base_datos: str = ""
) -> dict[str, Any]:
    """
    Punto de entrada principal. Detecta el tipo de URL y rutea al extractor
    correspondiente. Retorna dict normalizado con metadatos.
    """
    url_or_doi = url_or_doi.strip()
    url_type = _classify_url(url_or_doi)
    logger.info("URL clasificada como '%s': %s", url_type, url_or_doi[:80])

    metadata = None

    if url_type == "doi":
        metadata = _extract_via_doi(url_or_doi)

    elif url_type == "arxiv":
        metadata = _extract_arxiv(url_or_doi)
        # Fallback: intentar OpenAlex con el DOI de arXiv
        if not metadata or not metadata.get("abstract"):
            arxiv_id = _extract_arxiv_id(url_or_doi)
            if arxiv_id:
                oa = _extract_openalex(f"10.48550/arXiv.{arxiv_id}")
                if oa:
                    if not metadata:
                        metadata = oa
                    elif not metadata.get("abstract") and oa.get("abstract"):
                        metadata["abstract"] = oa["abstract"]

    elif url_type == "github":
        metadata = _extract_github(url_or_doi)

    elif url_type == "pdf":
        metadata = _extract_remote_pdf(url_or_doi)

    elif url_type == "web":
        metadata = _extract_web(url_or_doi)

    if metadata and metadata.get("titulo"):
        metadata["base_datos"] = base_datos
        return metadata

    logger.warning("No se pudieron obtener metadatos para: %s", url_or_doi)
    return {
        "titulo": "",
        "autores": [],
        "anio": "",
        "journal": "",
        "doi": "",
        "abstract": "",
        "tipo": "",
        "url": url_or_doi,
        "base_datos": base_datos,
        "fuente_metadata": "ninguna",
        "error": f"Metadatos no disponibles para: {url_or_doi}",
    }


def _extract_via_doi(url_or_doi: str) -> dict[str, Any] | None:
    """Extrae metadatos vía DOI usando CrossRef + OpenAlex."""
    doi = extract_doi(url_or_doi)
    if not doi:
        return None

    logger.info("Extrayendo metadatos para DOI: %s", doi)

    # Intento 1: CrossRef
    metadata = _extract_crossref(doi)
    if metadata and metadata.get("titulo"):
        logger.info("Metadatos obtenidos de CrossRef")

        if not metadata.get("abstract"):
            logger.info("Abstract no disponible en CrossRef, buscando en OpenAlex...")
            oa_data = _extract_openalex(doi)
            if oa_data and oa_data.get("abstract"):
                metadata["abstract"] = oa_data["abstract"]
                logger.info("Abstract obtenido de OpenAlex")

        return metadata

    # Intento 2: OpenAlex
    logger.info("CrossRef falló o incompleto, intentando OpenAlex...")
    metadata = _extract_openalex(doi)
    if metadata and metadata.get("titulo"):
        logger.info("Metadatos obtenidos de OpenAlex")
        return metadata

    return None
