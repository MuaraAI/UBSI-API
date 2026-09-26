import pytest
from app.modules.news import parse_wp_posts, parse_wp_post_detail
from app.modules.repository import parse_repository_items
from app.modules.ejournal import parse_journal_catalog

def test_parse_wp_posts():
    sample_raw = [
        {
            "id": 101,
            "date": "2026-09-25T16:18:15",
            "link": "https://news.bsi.ac.id/berita/sample-post/",
            "title": {"rendered": "Tim Cilok Cinta UBSI Lolos KMI Expo XVII 2026"},
            "excerpt": {"rendered": "<p>Ringkasan berita singkat...</p>"},
            "_embedded": {
                "author": [{"name": "Fachrurozi"}],
                "wp:featuredmedia": [{"source_url": "https://news.bsi.ac.id/wp-content/uploads/foto.jpg"}]
            }
        }
    ]
    posts = parse_wp_posts(sample_raw)
    assert len(posts) == 1
    p = posts[0]
    assert p["id"] == "101"
    assert p["title"] == "Tim Cilok Cinta UBSI Lolos KMI Expo XVII 2026"
    assert p["author"] == "Fachrurozi"
    assert p["featured_image"] == "https://news.bsi.ac.id/wp-content/uploads/foto.jpg"
    assert "Ringkasan" in p["excerpt"]

def test_parse_wp_post_detail():
    sample_detail = {
        "id": 101,
        "date": "2026-09-25T16:18:15",
        "link": "https://news.bsi.ac.id/berita/sample-post/",
        "title": {"rendered": "Judul Lengkap"},
        "content": {"rendered": "<p>Paragraf isi berita...</p>"},
        "excerpt": {"rendered": "<p>Ringkasan...</p>"},
        "_embedded": {
            "author": [{"name": "Admin"}]
        }
    }
    d = parse_wp_post_detail(sample_detail)
    assert d["id"] == "101"
    assert d["title"] == "Judul Lengkap"
    assert "Paragraf isi" in d["content"]

def test_parse_repository_items():
    sample_html = """
    <div class="ep_view_blurb">
      <a href="https://repository.bsi.ac.id/index.php/repo/viewitem/1234">Sistem Informasi Penjualan</a> (2026)
    </div>
    <div class="ep_view_blurb">
      <a href="/index.php/repo/viewitem/5678">Analisis Algoritma K-Means</a> (2025)
    </div>
    """
    items = parse_repository_items(sample_html)
    assert len(items) == 2
    assert items[0]["id"] == "1234"
    assert items[0]["title"] == "Sistem Informasi Penjualan"
    assert items[1]["id"] == "5678"

def test_parse_journal_catalog():
    sample_html = """
    <ul>
      <li><a href="/ejurnal/index.php/Bianglala/">Bianglala Informatika</a></li>
      <li><a href="/ejurnal/index.php/wanastra/">Wanastra: Jurnal Bahasa dan Sastra</a></li>
      <li><a href="https://ejournal.bsi.ac.id/ejurnal/index.php/khatulistiwa/">Jurnal Khatulistiwa</a></li>
    </ul>
    """
    catalog = parse_journal_catalog(sample_html)
    assert len(catalog) == 3
    assert catalog[0]["slug"] == "bianglala"
    assert catalog[1]["slug"] == "wanastra"
    assert catalog[2]["slug"] == "khatulistiwa"
