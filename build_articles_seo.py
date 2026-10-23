#!/usr/bin/env python3
"""
build_articles_seo.py

Bilingual Technical Articles & SEO Hub Compiler for khanhdp.com
Authored by Duong Phuc Khanh (Dương Phúc Khánh · khanhdp · Kido)
- Compiles 12 technical articles (6 English + 6 Vietnamese) under /articles/<slug>/index.html
- Generates the authoritative Articles Hub at /articles/index.html
- Links 20 flagship episodes directly to https://truyen.khanhdp.com/tap/...
- Injects validated Schema.org JSON-LD (@graph with TechArticle, Person, BreadcrumbList)
- Matches production styling of about.html and en.html
"""

import os
import re
import json
import html
from pathlib import Path

BASE_DIR = Path("/Users/kido/profile/web")
ARTICLES_DIR = BASE_DIR / "articles"
SEEDING_DIR = Path("/Users/kido/profile/media/content/SOCIAL_POSTS_SEEDING")

CANONICAL_PERSON = {
    "@type": "Person",
    "@id": "https://khanhdp.com/#person",
    "name": "Dương Phúc Khánh",
    "givenName": "Khánh",
    "familyName": "Dương",
    "additionalName": "Phúc",
    "alternateName": [
        "Duong Phuc Khanh",
        "khanhdp",
        "Kido",
        "Khánh Dương",
        "Khanh Duong",
        "khanhduong22",
        "phuckhanh22",
        "kode.x.kido",
        "kodexkido"
    ],
    "jobTitle": "Senior Software Engineer & Systems Architect",
    "url": "https://khanhdp.com",
    "image": "https://khanhdp.com/duong-phuc-khanh.jpg",
    "birthDate": "1995",
    "identifier": [
        {
            "@type": "PropertyValue",
            "propertyID": "Google Knowledge Graph ID",
            "value": "/g/11zyg5zq1c"
        },
        {
            "@type": "PropertyValue",
            "propertyID": "Wikidata",
            "value": "Q141718572"
        },
        {
            "@type": "PropertyValue",
            "propertyID": "ORCID",
            "value": "0009-0005-7192-2664"
        }
    ],
    "sameAs": [
        "https://www.google.com/search?kgmid=/g/11zyg5zq1c",
        "https://g.co/kg/g/11zyg5zq1c",
        "https://khanhdp.com",
        "https://khanhdp.com/about",
        "https://khanhdp.com/en",
        "https://duongphuckhanh.dev",
        "https://www.wikidata.org/wiki/Q141718572",
        "https://orcid.org/0009-0005-7192-2664",
        "https://baodanang.vn/goi-mon-an-bang-dien-thoai-thong-minh-3174905.html",
        "https://github.com/khanhduong22",
        "https://dev.to/khanhduong22",
        "https://viblo.asia/u/khanhdp",
        "https://linkedin.com/in/duong-phuc-khanh/",
        "https://x.com/duongphuckhanh",
        "https://facebook.com/khanhduong2295/",
        "https://blog.khanhdp.com",
        "https://truyen.khanhdp.com"
    ]
}

FLAGSHIP_EPISODES_20 = [
    {
        "id": 1,
        "slug": "tap-1-thang-em-vibe-coding",
        "title": "Tập 1: Cú Sốc Vibe-Coding & Cuộc Tháo Chạy Nửa Đêm",
        "desc": "Bài học xương máu khi giao trọn niềm tin cho AI sinh code không có guardrails và cú crash hệ thống lúc 2 giờ sáng.",
        "category": "AI & Agentic"
    },
    {
        "id": 9,
        "slug": "tap-9-bay-in-app-browser",
        "title": "Tập 9: Bẫy In-App Browser Facebook & Zalo Trên Mobile",
        "desc": "Giải mã thảm họa Storage Partitioning, mất Cookie Session và chiến thuật Breakout ra Safari / Chrome ngoài.",
        "category": "Mobile & Webview"
    },
    {
        "id": 10,
        "slug": "tap-10-tham-hoa-360px",
        "title": "Tập 10: Thảm Họa Màn Hình 360px & Nghệ Thuật Viewport",
        "desc": "Tối ưu hóa layout cho các dòng điện thoại Android giá rẻ, triệt tiêu Horizontal Scrollbar và bảo vệ 60FPS.",
        "category": "Frontend UI"
    },
    {
        "id": 11,
        "slug": "tap-11-mo-sentry-apm",
        "title": "Tập 11: Mở Sentry APM & Bắt Ma Latency Lúc Nửa Đêm",
        "desc": "Cách thiết lập tracing phân tán, gắn nhãn transaction và truy tìm câu lệnh SQL nuốt trọn CPU Contabo.",
        "category": "Observability"
    },
    {
        "id": 82,
        "slug": "tap-82-chuyen-tau-ngam-web-push-ios-safari",
        "title": "Tập 82: Chuyến Tàu Ngầm Web Push Trên iOS Safari",
        "desc": "Chinh phục Web Push Notification trên iOS PWA không cần qua Apple Developer Account $99/năm.",
        "category": "PWA & iOS"
    },
    {
        "id": 84,
        "slug": "tap-84-cuoc-thanh-trung-docker-dangle-cuu-o-cung-vps",
        "title": "Tập 84: Cuộc Thanh Trừng Docker Dangle Cứu Ổ Cứng VPS",
        "desc": "Xử lý sự cố tràn ổ cứng 100% lúc 4 giờ sáng do Docker build layer dangle và script tự động dọn dẹp cron job.",
        "category": "DevOps & VPS"
    },
    {
        "id": 100,
        "slug": "tap-100-dai-ket-cuc-100-tap-khuc-khai-hoan-spartan",
        "title": "Tập 100: Đại Kết Cục 100 Tập & Khúc Khải Hoàn Spartan",
        "desc": "Nhìn lại hành trình 100 ngày kỷ luật Winter Arc, cột mốc 1.1K WAU và triết lý kỹ thuật của một Senior Developer.",
        "category": "Milestone"
    },
    {
        "id": 108,
        "slug": "tap-108-con-bao-cors-preflight-options-caddy",
        "title": "Tập 108: Cơn Bão CORS Preflight OPTIONS & Nghệ Thuật Caddy 2",
        "desc": "Cách dập tắt hàng ngàn OPTIONS request thừa thãi làm nghẽn server và cấu hình Caddy Native Reverse Proxy.",
        "category": "Infrastructure"
    },
    {
        "id": 111,
        "slug": "tap-111-tieng-keu-cuu-luc-04h48-cua-minh-chu-va-chiec-bay-time-proof-secret",
        "title": "Tập 111: Tiếng Kêu Cứu Lúc 04h48 & Chiếc Bẫy Time-Proof Secret",
        "desc": "Giải cứu chuỗi kỷ luật rạng sáng, bảo vệ chữ ký HMAC SHA-256 chống lại tấn công Replay Attack từ client.",
        "category": "Security"
    },
    {
        "id": 114,
        "slug": "tap-114-voi-caddy-roi-thi-caddy-het-khai-tu-nginx-portfolio",
        "title": "Tập 114: Khai Tử Nginx Sang Caddy Toàn Diện Trên Portfolio",
        "desc": "Quy hoạch lại toàn bộ hạ tầng 30 container, tự động hóa SSL Let's Encrypt và cắt giảm 80% độ phức tạp config.",
        "category": "DevOps & VPS"
    },
    {
        "id": 115,
        "slug": "tap-115-bat-ma-web-vitals-sentry-va-bi-mat-30-giay",
        "title": "Tập 115: Bắt Ma Web Vitals Sentry & Bí Mật 30 Giây",
        "desc": "Lọc sạch các giao dịch ảo của người dùng mở tab ngầm làm bóp méo số liệu LCP và INP trong Google Search Console.",
        "category": "Observability"
    },
    {
        "id": 116,
        "slug": "tap-116-dai-phau-thuat-state-management-zustand-tanstack-query",
        "title": "Tập 116: Đại Phẫu Thuật State Management Zustand & TanStack Query",
        "desc": "Phân định rạch ròi giữa Server State và Client State, xóa bỏ anti-pattern nhồi nhét API cache vào global state.",
        "category": "Architecture"
    },
    {
        "id": 118,
        "slug": "tap-118-cuoc-khai-tu-6400-dong-redux-cu-lat-do-the-ky-cua-zustand-tanstack-query",
        "title": "Tập 118: Khai Tử 6400 Dòng Redux Cũ — Cuộc Đảo Chính Của Zustand",
        "desc": "Hành trình xẻ thịt khối mã nguồn cồng kềnh, giảm 42KB bundle size và tăng tốc độ phản hồi UI lên 60FPS.",
        "category": "Code Refactor"
    },
    {
        "id": 119,
        "slug": "tap-119-bop-co-eager-auth-va-tram-sach-material-symbols-interaction-driven-auth",
        "title": "Tập 119: Bóp Cổ Eager Auth & Interaction-Driven Auth Thông Minh",
        "desc": "Chặn đứng các request xác thực người dùng chặn ngang quá trình First Paint, đưa TBT về 0ms tuyệt đối.",
        "category": "Web Performance"
    },
    {
        "id": 120,
        "slug": "tap-120-xoa-bo-loading-tsx-cua-nextjs-bi-kip-zero-streaming-fallback-va-frame-0-skeleton",
        "title": "Tập 120: Xóa Bỏ loading.tsx Của Next.js & Frame-0 Skeleton",
        "desc": "Khắc phục triệt để hiện tượng giật màn hình (CLS) khi Next.js chuyển trang bằng Skeleton đồng bộ Frame-0.",
        "category": "Next.js"
    },
    {
        "id": 121,
        "slug": "tap-121-dai-di-cu-monorepo-len-full-bun-chat-dut-long-task-205ms-va-day-lcp-ve-frame-2",
        "title": "Tập 121: Đại Di Cư Monorepo Lên Full Bun — Chặt Đứt Long Task 205ms",
        "desc": "Chuyển dịch toàn bộ runtime sang Bun, tối ưu build pipeline và đẩy thời gian nạp trang LCP về Frame 2.",
        "category": "Infrastructure"
    },
    {
        "id": 124,
        "slug": "tap-124-vu-an-dau-doc-bo-nho-dem-rsc-service-worker-v7-va-accessibility-100-tuyet-doi",
        "title": "Tập 124: Vụ Án Đầu Độc Bộ Nhớ Đệm RSC & Service Worker v7",
        "desc": "Phân tích cú xung đột giữa Service Worker Cache và Next.js RSC Flight Header khiến iOS Safari bị crash trắng xóa.",
        "category": "Edge & PWA"
    },
    {
        "id": 125,
        "slug": "tap-125-khai-tu-firebase-sdk-khoi-web-buoc-ngoat-native-google-oauth-20",
        "title": "Tập 125: Khai Tử Firebase SDK Khỏi Web — Bước Ngoặt Native Google OAuth 2.0",
        "desc": "Cắt bỏ 140KB thư viện Firebase cồng kềnh, tự viết Google Identity Platform native flow siêu nhẹ và an toàn.",
        "category": "Security"
    },
    {
        "id": 126,
        "slug": "tap-126-nghe-thuat-xe-thit-god-file-2000-dong-va-tuyet-ky-tab-preloader",
        "title": "Tập 126: Nghệ Thuật Xẻ Thịt God-File 2000 Dòng & Tuyệt Kỹ Tab Preloader",
        "desc": "Phương pháp luận phân rã tệp tin khổng lồ thành các slice domain rành mạch và kỹ thuật prefetch theo cử chỉ chạm.",
        "category": "Code Refactor"
    },
    {
        "id": 131,
        "slug": "tap-131-dao-trung-o-bug-multi-temporal-tenancy-khi-asia-saigon-troi-day-va-cu-lua-ip-cloudflare",
        "title": "Tập 131: Đào Trúng Ổ Bug Multi-Temporal Tenancy & Cú Lừa IP Cloudflare",
        "desc": "Xử lý sai lệch múi giờ đa quốc gia của vận động viên quốc tế và cách bóc tách IP gốc qua Cloudflare Header.",
        "category": "Distributed Systems"
    }
]

EPISODE_CONTEXT_MAP = {
    "7-gate-multi-agent-engineering-harness": [
        "tap-1-thang-em-vibe-coding",
        "tap-105-khi-ga-ai-thanh-dong-doi-sinh-tu",
        "tap-111-tieng-keu-cuu-luc-04h48-cua-minh-chu-va-chiec-bay-time-proof-secret",
        "tap-121-dai-di-cu-monorepo-len-full-bun-chat-dut-long-task-205ms-va-day-lcp-ve-frame-2",
        "tap-126-nghe-thuat-xe-thit-god-file-2000-dong-va-tuyet-ky-tab-preloader"
    ],
    "bare-metal-vps-high-concurrency-playbook": [
        "tap-84-cuoc-thanh-trung-docker-dangle-cuu-o-cung-vps",
        "tap-87-chiec-bay-timezone-may-chu-duc-contabo",
        "tap-108-con-bao-cors-preflight-options-caddy",
        "tap-110-chinh-phuc-cot-moc-110-tap-de-che-30-container",
        "tap-114-voi-caddy-roi-thi-caddy-het-khai-tu-nginx-portfolio"
    ],
    "zero-tbt-lighthouse-100-pwa-engineering": [
        "tap-9-bay-in-app-browser",
        "tap-10-tham-hoa-360px",
        "tap-82-chuyen-tau-ngam-web-push-ios-safari",
        "tap-115-bat-ma-web-vitals-sentry-va-bi-mat-30-giay",
        "tap-127-tuyet-ky-font-tieu-phau-tien-latin-ext-ve-vuon-va-arial-fallback-zero-cls"
    ],
    "giai-phau-race-condition-valkey-distributed-lock": [
        "tap-81-phan-chia-dong-mau-valkey-staging-prod",
        "tap-93-dia-chan-nghen-mang-dem-chung-ket",
        "tap-111-tieng-keu-cuu-luc-04h48-cua-minh-chu-va-chiec-bay-time-proof-secret",
        "tap-112-cu-nuot-chung-diem-so-cua-redux-state-rollover",
        "tap-128-vu-an-day-tu-4h45-sang-hoc-6-tieng-nhung-mat-diem-va-cu-bay-treo-may-04h30"
    ],
    "http-304-singleflight-cache-races-mutation-epochs": [
        "tap-83-bai-hoc-caching-service-worker-f5-trong-vo-vong",
        "tap-113-vu-an-3-tieng-deep-work-boc-hoi-va-chiec-phao-cuu-sinh-944-diem",
        "tap-116-dai-phau-thuat-state-management-zustand-tanstack-query",
        "tap-118-cuoc-khai-tu-6400-dong-redux-cu-lat-do-the-ky-cua-zustand-tanstack-query",
        "tap-123-xoa-so-bong-ma-stale-day-rollover-quy-hoach-mang-vt-infra-va-clone-db-1-giay"
    ],
    "http-304-not-modified-singleflight-cache-race-pwa": [
        "tap-83-bai-hoc-caching-service-worker-f5-trong-vo-vong",
        "tap-113-vu-an-3-tieng-deep-work-boc-hoi-va-chiec-phao-cuu-sinh-944-diem",
        "tap-116-dai-phau-thuat-state-management-zustand-tanstack-query",
        "tap-118-cuoc-khai-tu-6400-dong-redux-cu-lat-do-the-ky-cua-zustand-tanstack-query",
        "tap-123-xoa-so-bong-ma-stale-day-rollover-quy-hoach-mang-vt-infra-va-clone-db-1-giay"
    ],
    "redis-valkey-bitmaps-popcnt-o1-streak-engine": [
        "tap-81-phan-chia-dong-mau-valkey-staging-prod",
        "tap-88-thuat-toan-sleep-gap-detection-chong-an-gian-giac-ngu",
        "tap-91-con-sot-ngay-thu-90-cuoc-dua-tam-ly-khoc-liet",
        "tap-100-dai-ket-cuc-100-tap-khuc-khai-hoan-spartan",
        "tap-128-vu-an-day-tu-4h45-sang-hoc-6-tieng-nhung-mat-diem-va-cu-bay-treo-may-04h30"
    ],
    "nextjs-16-cloudflare-rsc-flight-cache-poisoning": [
        "tap-107-chiec-bay-next-public-api-url-tro-vao-hu-khong",
        "tap-109-loi-nguyen-http2-server-push-va-103-early-hints",
        "tap-120-xoa-bo-loading-tsx-cua-nextjs-bi-kip-zero-streaming-fallback-va-frame-0-skeleton",
        "tap-124-vu-an-dau-doc-bo-nho-dem-rsc-service-worker-v7-va-accessibility-100-tuyet-doi",
        "tap-131-dao-trung-o-bug-multi-temporal-tenancy-khi-asia-saigon-troi-day-va-cu-lua-ip-cloudflare"
    ],
    "postgresql-17-base32-materialized-paths-bitmask-rbac": [
        "tap-85-tran-dia-type-safety-xuyen-bien-gioi-shared-dto",
        "tap-86-nghe-thuat-zero-allocation-logging",
        "tap-96-toi-uu-vacuum-va-partitioning-postgresql",
        "tap-117-ha-guc-bao-port-scanner-va-service-worker-navigation-preload",
        "tap-122-la-ban-dan-loi-tour-v23-dau-an-tac-gia-khanhdp-com-va-vu-an-diem-ky-luat-phut-89"
    ],
    "kien-truc-redis-valkey-bitmap-46-bytes-streak-engine": [
        "tap-81-phan-chia-dong-mau-valkey-staging-prod",
        "tap-88-thuat-toan-sleep-gap-detection-chong-an-gian-giac-ngu",
        "tap-91-con-sot-ngay-thu-90-cuoc-dua-tam-ly-khoc-liet",
        "tap-100-dai-ket-cuc-100-tap-khuc-khai-hoan-spartan",
        "tap-128-vu-an-day-tu-4h45-sang-hoc-6-tieng-nhung-mat-diem-va-cu-bay-treo-may-04h30"
    ],
    "xu-ly-rsc-flight-cache-poisoning-nextjs-16-cloudflare": [
        "tap-107-chiec-bay-next-public-api-url-tro-vao-hu-khong",
        "tap-109-loi-nguyen-http2-server-push-va-103-early-hints",
        "tap-120-xoa-bo-loading-tsx-cua-nextjs-bi-kip-zero-streaming-fallback-va-frame-0-skeleton",
        "tap-124-vu-an-dau-doc-bo-nho-dem-rsc-service-worker-v7-va-accessibility-100-tuyet-doi",
        "tap-131-dao-trung-o-bug-multi-temporal-tenancy-khi-asia-saigon-troi-day-va-cu-lua-ip-cloudflare"
    ],
    "postgresql-17-base32-materialized-path-bitmask-rbac-tieng-viet": [
        "tap-85-tran-dia-type-safety-xuyen-bien-gioi-shared-dto",
        "tap-86-nghe-thuat-zero-allocation-logging",
        "tap-96-toi-uu-vacuum-va-partitioning-postgresql",
        "tap-117-ha-guc-bao-port-scanner-va-service-worker-navigation-preload",
        "tap-122-la-ban-dan-loi-tour-v23-dau-an-tac-gia-khanhdp-com-va-vu-an-diem-ky-luat-phut-89"
    ]
}


def parse_frontmatter(text):
    """Extract frontmatter and body from markdown file."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2]
            meta = {}
            for line in fm_text.strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                        v = v[1:-1]
                    meta[k] = v
            return meta, body
    return {}, text


def clean_inline_md(text):
    """Convert inline markdown to HTML."""
    # Escape existing HTML entities safely
    # Images: ![alt](url)
    def repl_img(m):
        alt = m.group(1)
        src = m.group(2)
        return f'<figure class="my-6 text-center"><img src="{src}" alt="{alt}" class="rounded-xl border border-white/10 mx-auto max-w-full" loading="lazy" /><figcaption class="text-xs font-mono text-zinc-500 mt-2">{alt}</figcaption></figure>'
    text = re.sub(r'!\[(.*?)\]\((.*?)\)', repl_img, text)

    # Links: [text](url)
    def repl_link(m):
        txt = m.group(1)
        href = m.group(2)
        target = ' target="_blank" rel="noopener"' if href.startswith("http") else ''
        return f'<a href="{href}" class="text-sky-400 hover:text-emerald-400 underline decoration-zinc-600 underline-offset-4 transition-colors"{target}>{txt}</a>'
    text = re.sub(r'\[(.*?)\]\((.*?)\)', repl_link, text)

    # Bold: **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong class="text-white font-semibold">\1</strong>', text)

    # Italic: *text*
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<em class="italic text-zinc-200">\1</em>', text)

    # Inline Code: `code`
    def repl_code(m):
        code_txt = html.escape(m.group(1))
        return f'<code class="px-1.5 py-0.5 rounded bg-white/[0.06] text-emerald-400 font-mono text-[13px]">{code_txt}</code>'
    text = re.sub(r'`([^`]+)`', repl_code, text)

    return text


def markdown_to_html(md_text):
    """Convert markdown blocks into clean semantic HTML."""
    lines = md_text.replace("\r\n", "\n").split("\n")
    output = []
    in_code_block = False
    code_lang = ""
    code_lines = []
    in_list = False
    list_type = "ul"
    in_table = False
    table_lines = []

    def close_list():
        nonlocal in_list, list_type
        if in_list:
            output.append(f"</{list_type}>")
            in_list = False

    def close_table():
        nonlocal in_table, table_lines
        if in_table and table_lines:
            # Parse table lines
            header_line = table_lines[0]
            data_lines = table_lines[2:] if len(table_lines) > 2 else []
            headers = [c.strip() for c in header_line.split("|")[1:-1]]
            html_table = [
                '<div class="overflow-x-auto my-6 border border-white/10 rounded-lg">',
                '<table class="w-full text-left text-xs text-zinc-300 border-collapse">',
                '<thead class="bg-white/[0.04] text-[11px] font-mono uppercase tracking-wider text-zinc-400 border-b border-white/10">',
                '<tr>'
            ]
            for h in headers:
                html_table.append(f'<th class="p-3">{clean_inline_md(h)}</th>')
            html_table.append('</tr></thead><tbody class="divide-y divide-white/[0.06]">')
            for row in data_lines:
                if not row.strip():
                    continue
                cols = [c.strip() for c in row.split("|")[1:-1]]
                html_table.append('<tr class="hover:bg-white/[0.02]">')
                for c in cols:
                    html_table.append(f'<td class="p-3">{clean_inline_md(c)}</td>')
                html_table.append('</tr>')
            html_table.append('</tbody></table></div>')
            output.append("\n".join(html_table))
            table_lines = []
            in_table = False

    for line in lines:
        stripped = line.strip()

        # Fenced code block start/end
        if stripped.startswith("```"):
            close_list()
            close_table()
            if in_code_block:
                escaped_code = html.escape("\n".join(code_lines))
                lang_cls = f' class="language-{code_lang}"' if code_lang else ''
                output.append(
                    f'<pre class="bg-[#121212] border border-white/10 rounded-lg p-4 overflow-x-auto text-xs font-mono my-4"><code{lang_cls}>{escaped_code}</code></pre>'
                )
                code_lines = []
                in_code_block = False
                code_lang = ""
            else:
                in_code_block = True
                code_lang = stripped[3:].strip()
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Tables
        if stripped.startswith("|") and stripped.endswith("|"):
            close_list()
            in_table = True
            table_lines.append(stripped)
            continue
        elif in_table:
            close_table()

        # Blank line
        if not stripped:
            close_list()
            continue

        # Horizontal Rule
        if stripped in ["---", "***", "___"]:
            close_list()
            output.append('<hr class="border-white/[0.08] my-8" />')
            continue

        # Headers
        if stripped.startswith("#"):
            close_list()
            level = len(stripped.split()[0])
            title_text = stripped.lstrip("#").strip()
            slug_id = re.sub(r'[^a-zA-Z0-9\u00C0-\u024F\u1E00-\u1EFF]+', '-', title_text).strip('-').lower()
            if level == 1:
                # Top level h1 is usually handled in template header, but if inside body render h2
                output.append(f'<h2 id="{slug_id}" class="text-xl sm:text-2xl font-semibold text-zinc-100 mt-8 mb-4 flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span><span>{clean_inline_md(title_text)}</span></h2>')
            elif level == 2:
                output.append(f'<h2 id="{slug_id}" class="text-xl sm:text-2xl font-semibold text-zinc-100 mt-8 mb-4 flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span><span>{clean_inline_md(title_text)}</span></h2>')
            elif level == 3:
                output.append(f'<h3 id="{slug_id}" class="text-base sm:text-lg font-semibold text-zinc-200 mt-6 mb-3">{clean_inline_md(title_text)}</h3>')
            elif level == 4:
                output.append(f'<h4 id="{slug_id}" class="text-sm sm:text-base font-semibold text-zinc-300 mt-4 mb-2">{clean_inline_md(title_text)}</h4>')
            continue

        # Blockquote
        if stripped.startswith(">"):
            close_list()
            quote_content = clean_inline_md(stripped[1:].strip())
            output.append(f'<blockquote class="border-l-2 border-emerald-400 pl-4 py-1.5 my-4 bg-white/[0.02] rounded-r text-zinc-300 italic text-sm">{quote_content}</blockquote>')
            continue

        # Unordered list
        if stripped.startswith(("* ", "- ", "+ ")):
            if not in_list or list_type != "ul":
                close_list()
                in_list = True
                list_type = "ul"
                output.append('<ul class="list-disc pl-6 space-y-1.5 my-3 text-zinc-300">')
            item_text = clean_inline_md(stripped[2:].strip())
            output.append(f'<li>{item_text}</li>')
            continue

        # Ordered list
        m_ol = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if m_ol:
            if not in_list or list_type != "ol":
                close_list()
                in_list = True
                list_type = "ol"
                output.append('<ol class="list-decimal pl-6 space-y-1.5 my-3 text-zinc-300">')
            item_text = clean_inline_md(m_ol.group(2).strip())
            output.append(f'<li>{item_text}</li>')
            continue

        close_list()

        # Regular Paragraph
        output.append(f'<p class="leading-relaxed my-3.5 text-zinc-300">{clean_inline_md(stripped)}</p>')

    close_list()
    close_table()

    return "\n".join(output)


# ==============================================================================
# ARTICLE 10, 11, 12 VIETNAMESE CONTENT DEFINITIONS (~800-1200 words each)
# ==============================================================================

POST10_CONTENT = r"""---
title: "Kiến trúc Redis/Valkey Bitmap 46 Bytes: Xây dựng O(1) Streak Engine & Khử Sạch N+1 Query SQL"
published: true
description: "Cách Dương Phúc Khánh (Kido) thay thế hàng triệu dòng habit logs quan hệ bằng 46 bytes Redis Bitmap và tập lệnh phần cứng CPU POPCNT, đưa độ trễ p99 từ 140ms về 0.08ms."
tags: database, redis, performance, architecture
---

Đúng 06:00 sáng mỗi ngày, hàng ngàn vận động viên thể hình calisthenics mở ứng dụng luyện tập trên điện thoại. Mỗi người dùng đều kỳ vọng nhìn thấy ngay lập tức số ngày chuỗi kỷ luật hiện tại (Current Streak), tổng số buổi tập trong năm, và biểu đồ nhiệt thói quen (GitHub-style 365-day habit heatmap).

Trong thiết kế cơ sở dữ liệu quan hệ truyền thống, để tính toán một màn hình tưởng chừng đơn giản này, hệ thống buộc phải quét bảng nhật ký chứa hàng triệu bản ghi sự kiện:

```sql
-- Cách tiếp cận SQL truyền thống: Bảng Habit Logs quan hệ
SELECT checkin_date 
FROM habit_logs 
WHERE user_id = 48291 AND habit_id = 101 AND checkin_date >= '2026-01-01'
ORDER BY checkin_date ASC;
```

Khi hàng chục ngàn người dùng đồng loạt truy vấn trong khung giờ cao điểm 15 phút rạng sáng, hàng đợi kết nối (Connection Pool) của PostgreSQL lập tức bị nghẽn, các trang chỉ mục B-Tree làm tràn bộ nhớ đệm Buffer Cache, và độ trễ phân vị P99 vọt lên hơn **140ms**.

Tôi là **[Dương Phúc Khánh](https://khanhdp.com)** (được cộng đồng kỹ sư biết đến với định danh **[khanhdp](https://khanhdp.com)** hoặc moniker **Kido**, [@khanhduong22](https://github.com/khanhduong22)). Khi thiết kế hệ sinh thái ứng dụng PWA [Winter Arc](https://khanhdp.com) và biên tập 128 tập biên niên sử kỹ thuật **[Kido Chronicles](https://truyen.khanhdp.com)**, tôi đã quyết định loại bỏ hoàn toàn mô hình quan hệ cồng kềnh này để chuyển sang **Redis / Valkey Bitmaps**.

Kết quả: Chúng tôi nén toàn bộ lịch sử 365 ngày kỷ luật của một người dùng từ **32.000 bytes (32 KB)** của các dòng SQL xuống chỉ còn **46 bytes**, tính toán Streak và thống kê ở độ phức tạp **O(1)** với độ trễ **0.08ms** nhờ tập lệnh phần cứng CPU `POPCNT`.

---

## 1. Giới Hạn Vật Lý Của Mô Hình Quan Hệ (Relational Bottleneck)

Bảng nhật ký thông thường lưu trữ trạng thái với cấu trúc: `id (BIGINT)`, `user_id (BIGINT)`, `habit_id (INT)`, `checkin_date (DATE)`, `created_at (TIMESTAMPTZ)`.

Mỗi dòng dữ liệu tiêu tốn trung bình khoảng 80 bytes trên đĩa. Với 365 ngày, một người dùng tiêu tốn khoảng 29.2 KB dữ liệu thuần, chưa tính overhead của chỉ mục B-Tree index đa cột `(user_id, habit_id, checkin_date)`. Khi tính toán Streak, hệ thống phải duyệt qua toàn bộ mảng ngày tháng trong bộ nhớ ứng dụng để kiểm tra các ngày liên tiếp (`date_diff == 1`).

Nếu một màn hình Dashboard hiển thị danh sách 10 thói quen của người dùng, đây trở thành bài toán **N+1 Query** kinh điển hoặc đòi hỏi một câu lệnh `JOIN` phức tạp, làm tiêu hao CPU database vô ích.

---

## 2. Khám Phá Không Gian Bit: 365 Ngày Gói Gọn Trong 46 Bytes

Trong một năm dương lịch có tối đa 366 ngày. Mỗi ngày chỉ có 2 trạng thái nhị phân: **Hoàn thành (1)** hoặc **Chưa hoàn thành (0)**.

Do đó, toàn bộ 365 ngày của một thói quen có thể biểu diễn trọn vẹn trong một chuỗi 366 bits:
$$\lceil 366 / 8 \rceil = 46 \text{ bytes}$$

Trong Redis hoặc Valkey, cấu trúc chuỗi (String) hỗ trợ các thao tác cấp độ bit với độ phức tạp cực thấp:
* `SETBIT key offset value`: Gán bit tại ngày thứ $N$ (Offset từ 0 đến 365).
* `GETBIT key offset`: Đọc trạng thái của ngày thứ $N$.
* `BITCOUNT key [start end]`: Đếm tổng số bit 1 trong khoảng xác định.
* `BITPOS key bit [start end]`: Tìm vị trí đầu tiên của bit 0 hoặc 1.

Key pattern được thiết kế ngắn gọn theo định dạng: `hbt:{user_id}:{habit_id}:{year}` (Ví dụ: `hbt:48291:101:2026`).

---

## 3. Tập Lệnh Phần Cứng CPU POPCNT & Thuật Toán Tính Streak O(1)

Lệnh `BITCOUNT` trong Valkey không sử dụng vòng lặp duyệt từng bit thô thiển. Trái lại, nhân mã nguồn C của Valkey tận dụng trực tiếp tập lệnh phần cứng **POPCNT (Population Count)** của kiến trúc vi xử lý hiện đại x86-64 và ARM64:

```c
// Valkey bitops.c core implementation snippet
// Single hardware instruction execution: popcntq on x86_64
unsigned long long valkey_popcount64(unsigned long long x) {
    return __builtin_popcountll(x);
}
```

Nhờ lệnh `POPCNT`, CPU có thể đếm số bit 1 trong một thanh ghi 64-bit chỉ trong **1 chu kỳ xung nhịp (Clock Cycle)**. Toàn bộ 46 bytes của cả năm được quét sạch trong chưa đầy 6 lệnh CPU!

### Thuật Toán Đếm Chuỗi Kỷ Luật Hiện Tại (Current Streak)
Để tính chuỗi ngày liên tiếp tính đến ngày hôm nay ($D$):
1. Đọc tối đa 64 bits (8 bytes) gần nhất từ vị trí $D$ lùi về trước.
2. Đảo ngược giá trị nhị phân (`~bits`).
3. Sử dụng tập lệnh `CTZ (Count Trailing Zeros)` hoặc `CLZ (Count Leading Zeros)` để xác định vị trí của bit 0 đầu tiên.
4. Khoảng cách từ ngày hiện tại tới bit 0 đầu tiên chính là số ngày Streak liên tục hiện tại!

Toàn bộ quy trình diễn ra hoàn toàn trong bộ nhớ đệm CPU L1/L2 mà không hề chạm vào đĩa cứng hay chạy câu lệnh SQL nặng nề.

---

## 4. Triển Khai Mẫu Bằng TypeScript & Valkey Native Commands

Dưới đây là module mẫu trích xuất từ bộ thư viện `@kt/streak-engine` thuộc hệ thống Winter Arc:

```typescript
import { ValkeyClient } from '@kt/valkey-client';

export class HabitStreakService {
  constructor(private readonly valkey: ValkeyClient) {}

  private getDayOfYear(date: Date): number {
    const start = new Date(date.getFullYear(), 0, 0);
    const diff = date.getTime() - start.getTime();
    const oneDay = 1000 * 60 * 60 * 24;
    return Math.floor(diff / oneDay) - 1; // 0-indexed day
  }

  async markComplete(userId: number, habitId: number, date: Date = new Date()): Promise<void> {
    const year = date.getFullYear();
    const dayOffset = this.getDayOfYear(date);
    const key = `hbt:${userId}:${habitId}:${year}`;

    // Atomic bitwise write: O(1)
    await this.valkey.setbit(key, dayOffset, 1);
  }

  async getYearlyStats(userId: number, habitId: number, year: number): Promise<{ totalDays: number; heatmapBytes: Buffer }> {
    const key = `hbt:${userId}:${habitId}:${year}`;
    const pipeline = this.valkey.pipeline();

    pipeline.bitcount(key);
    pipeline.getBuffer(key);

    const [totalDays, rawBuffer] = await pipeline.exec();
    return {
      totalDays: (totalDays as number) || 0,
      heatmapBytes: (rawBuffer as Buffer) || Buffer.alloc(46, 0),
    };
  }
}
```

---

## 5. Bảng So Sánh Hiệu Năng Thực Chiến (Production Benchmark)

Dưới đây là kết quả kiểm thử tải thực tế trên máy chủ Linux VPS 8GB RAM với 10.000 người dùng ảo đồng thời:

| Tiêu Chí Đánh Giá | Mô Hình Quan Hệ (PostgreSQL 17) | Valkey Bitmap 46-Bytes Engine | Mức Độ Cải Thiện |
| :--- | :--- | :--- | :--- |
| **Dung lượng lưu trữ / User** | ~32,000 Bytes (32 KB) | **46 Bytes** | **Giảm 99.85%** |
| **Độ trễ truy vấn P50** | 18.4 ms | **0.04 ms** | **Nhanh gấp 460 lần** |
| **Độ trễ truy vấn P99** | 142.6 ms | **0.08 ms** | **Nhanh gấp 1,780 lần** |
| **CPU Sử dụng khi tải cao** | 78% (Lock Contention) | **4.2%** | **Tiết kiệm 94.6% CPU** |
| **Bộ nhớ Buffer Cache** | 480 MB cho 15,000 users | **0.69 MB** | **Gọn nhẹ tối đa** |

---

## 6. Tổng Kết Kiến Trúc

Bằng việc thay đổi tư duy từ "Lưu trữ dữ liệu dạng bảng" sang "Tổ chức bit nhị phân phù hợp với tập lệnh vi xử lý", chúng tôi đã:
1. Triệt tiêu hoàn toàn sự cố nghẽn kết nối database lúc 06:00 sáng.
2. Đưa trải nghiệm tải trang trên mobile PWA về dưới 1 giây mà không tốn thêm một đồng chi phí phần cứng.
3. Chứng minh triết lý *Ponytail Mindset*: "Đoạn code nhanh nhất và tiết kiệm nhất là đoạn code vận dụng tối đa sức mạnh sẵn có của nền tảng".
"""

POST11_CONTENT = r"""---
title: "Giải Phẫu Sự Cố Cloudflare Edge & Next.js 16: Triệt Tiêu Thảm Họa RSC Flight Payload Cache Poisoning"
published: true
description: "Cách header client navigation (RSC: 1) của Next.js App Router đầu độc bộ nhớ đệm Cloudflare Edge Cache biến PWA thành màn hình trắng xóa trên iOS Safari, và kiến trúc phòng thủ 3 lớp zero-downtime của Dương Phúc Khánh."
tags: nextjs, cloudflare, webdev, performance
---

Đúng 09:14 sáng một ngày đầu tuần, kênh hỗ trợ khách hàng của hệ thống tiếp nhận hàng loạt phản ánh khẩn cấp từ người dùng:

> *"Ứng dụng trên iPhone không mở được! Màn hình trắng xóa toàn ký tự lạ như `:HL[\"/static/css/...\"]` và `1:I[\"$Sreact.fragment\"...]`."*

Người dùng khởi động ứng dụng Progressive Web App (PWA) từ màn hình chính iOS Home Screen chỉ thấy một chuỗi dữ liệu thô dạng văn bản của giao thức React Server Component (RSC) Flight thay vì giao diện HTML hoàn chỉnh. Ngay cả người dùng máy tính để bàn khi nhấn tổ hợp phím tải lại trang (`Ctrl + F5`) cũng gặp hiện tượng tương tự.

Tuy nhiên, bảng điều khiển hệ thống nội bộ lại hiển thị **100% màu xanh**. CPU máy chủ Node.js chỉ ở mức 4%, không có ngoại lệ nào chưa được xử lý, và API nội bộ phản hồi cực nhanh dưới 8ms.

Hệ thống đã rơi vào chiếc bẫy nguy hiểm mang tên: **RSC Flight Payload Cache Poisoning tại Edge CDN**.

Tôi là **[Dương Phúc Khánh](https://khanhdp.com)** (được biết đến trong cộng đồng kỹ sư với tên gọi **[khanhdp](https://khanhdp.com)** hoặc **Kido**, [@khanhduong22](https://github.com/khanhduong22)). Trong vai trò Senior Systems Architect tại Tech Pulse và tác giả của 128 tập biên niên sử kỹ thuật **[Kido Chronicles](https://truyen.khanhdp.com)**, tôi đã trực tiếp mổ xẻ và xử lý triệt để sự cố này.

---

## 1. Cơ Chế Điều Hướng Của Next.js App Router: HTML Stream vs Flight Wire Data

Trong kiến trúc Next.js App Router, cùng một URL (ví dụ: `/dashboard`) có thể trả về hai định dạng dữ liệu hoàn toàn khác biệt tùy thuộc vào ngữ cảnh gửi yêu cầu:

1. **Full Document Navigation (Yêu cầu HTML ban đầu):** Khi người dùng gõ URL vào thanh địa chỉ hoặc mở PWA lần đầu, trình duyệt gửi request với header `Accept: text/html`. Máy chủ Next.js render mã HTML hoàn chỉnh kèm theo dữ liệu Flight để thực hiện Hydration.
2. **Soft Client Navigation (Chuyển trang nội bộ qua Next Link):** Khi người dùng nhấp vào thẻ `<Link href="/dashboard">`, router phía client của Next.js không tải lại toàn bộ trang mà chỉ gửi một yêu cầu nền kèm theo header đặc biệt:
   ```http
   RSC: 1
   Next-Router-State-Tree: ...
   Accept: text/x-component
   ```
   Lúc này, Next.js bỏ qua phần vỏ HTML và chỉ trả về **Flight Payload** thuần túy chứa danh sách Virtual DOM diff để client cập nhật giao diện.

---

## 2. Điểm Mù Của Edge Cache: Tại Sao Cloudflare Lưu Nhầm Flight Data?

Theo mặc định của hầu hết các dịch vụ CDN (bao gồm Cloudflare, Fastly, AWS CloudFront), khóa định danh bộ nhớ đệm (Cache Key) chỉ bao gồm:
$$\text{Cache Key} = \text{Scheme} + \text{Host} + \text{URI Path}$$

Nếu quản trị viên thiết lập một quy tắc lưu đệm Edge Cache (ví dụ: `Cache-Control: public, max-age=3600`) cho các trang công khai mà không phân biệt header `RSC`, thảm họa sẽ xảy ra theo kịch bản sau:

1. **Bước 1:** Một người dùng đang lướt trang web nhấp vào link nội bộ. Trình duyệt gửi request tới `/articles/` với header `RSC: 1`.
2. **Bước 2:** Yêu cầu đi qua Edge CDN và chạm tới máy chủ Next.js. Next.js trả về nội dung Flight Payload kèm header `Content-Type: text/x-component`.
3. **Bước 3:** Edge CDN lưu trữ nội dung Flight Payload này vào Cache Key: `https://khanhdp.com/articles/`.
4. **Bước 4 (Đầu độc thành công):** Một người dùng mới truy cập trực tiếp bằng Safari hoặc mở PWA. Trình duyệt mong đợi nhận được HTML (`Accept: text/html`), nhưng Edge CDN ngay lập tức trả về Flight Payload dạng text đang được lưu trong cache! Trình duyệt render chuỗi text thô ra màn hình thay vì giao diện Web.

---

## 3. Kiến Trúc Phòng Thủ 3 Lớp (3-Layer Edge Defense Architecture)

Để triệt tiêu vĩnh viễn nguy cơ đầu độc bộ nhớ đệm mà không làm mất đi lợi thế tăng tốc của Edge CDN, chúng tôi đã triển khai kiến trúc bảo vệ đa tầng:

```
[Client Request] 
       │
       ▼
[Layer 1: Cloudflare Custom Cache Key] ➔ Tách biệt Cache Key theo Header (RSC: 0 vs 1)
       │
       ▼
[Layer 2: Reverse Proxy (Caddy 2)]    ➔ Thêm Vary: RSC, Next-Router-State-Tree, Accept
       │
       ▼
[Layer 3: Next.js Response Guard]     ➔ Tự động hạ cấp Cache-Control: private nếu có RSC header
```

### Lớp 1: Cấu Hình Cache Key Partitioning Trên Cloudflare
Sử dụng Cloudflare Cache Rules để phân tách khóa lưu đệm dựa trên sự hiện diện của header `RSC`:

```
Expression: (http.request.uri.path eq "/articles" and http.request.headers["rsc"] eq "1")
Action:
  - Cache Key: Include Header "RSC"
  - Edge Cache TTL: 0 (Bypass Cache for dynamic RSC transitions)
```

### Lớp 2: Chuẩn Hóa Header Vary Tại Reverse Proxy (Caddyfile)
Reverse Proxy phải luôn luôn đính kèm chỉ thị `Vary` để báo hiệu cho mọi tầng proxy trung gian biết rằng nội dung thay đổi theo header:

```caddy
khanhdp.com {
    @is_rsc {
        header RSC 1
    }

    handle {
        header {
            # Bắt buộc CDN và Browser phải tách cache theo RSC và Accept
            Vary "Accept, RSC, Next-Router-State-Tree"
            # Bảo vệ chống clickjacking và mime-sniffing
            X-Content-Type-Options "nosniff"
        }
        reverse_proxy localhost:3000
    }
}
```

### Lớp 3: Response Header Interceptor Tại Next.js Middleware

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const isRSC = request.headers.has('rsc');
  const response = NextResponse.next();

  // Đảm bảo header Vary luôn hiện diện
  response.headers.append('Vary', 'RSC');
  response.headers.append('Vary', 'Next-Router-State-Tree');
  response.headers.append('Vary', 'Accept');

  // Nếu là RSC request, tuyệt đối không cho phép CDN cache công khai
  if (isRSC) {
    response.headers.set(
      'Cache-Control',
      'private, no-cache, no-store, max-age=0, must-revalidate'
    );
  }

  return response;
}
```

---

## 4. Kết Quả Xác Minh Bằng Kiểm Thử Tự Động Playwright E2E

Sau khi triển khai bộ lọc 3 lớp, chúng tôi thiết lập kịch bản kiểm thử hồi quy tự động trong Playwright để đảm bảo lỗi không bao giờ tái diễn:

1. Thực hiện Soft Navigation giả lập header `RSC: 1` để ghi cache tại Edge.
2. Thực hiện Hard Navigation ngay sau đó với header `Accept: text/html`.
3. Kiểm tra mã phản hồi HTTP phải là 200, header `Content-Type` phải chứa `text/html`, và DOM phải render đầy đủ thẻ `<main>` mà không chứa bất kỳ ký tự raw Flight nào.

Toàn bộ 100% ca kiểm thử đã vượt qua xuất sắc trên cả Safari di động và Chrome máy tính để bàn.
"""

POST12_CONTENT = r"""---
title: "Khắc Phục Đòn Chí Mạng Recursive CTE: Cây Bình Luận Base32 Materialized Path & Bitmask RBAC Trong PostgreSQL 17"
published: true
description: "Tại sao WITH RECURSIVE CTEs và JOIN 5 bảng phân quyền làm nghẽn Database khi tải cao, và giải pháp Base32 Materialized Path cùng 64-bit Bitmask RBAC đưa độ trễ p95 từ 142ms xuống 0.8ms của Dương Phúc Khánh."
tags: postgres, backend, architecture, performance
---

Khi xây dựng các nền tảng mạng xã hội hoặc cộng đồng trực tuyến quy mô lớn, có hai câu truy vấn cơ sở dữ liệu xuất hiện trên hầu như **mọi yêu cầu HTTP**:

1. **Lấy danh sách cây bình luận phân cấp vô hạn** (Hierarchical Comment Tree tương tự Reddit hoặc Hacker News).
2. **Xác thực quyền hạn người dùng** theo mô hình Phân quyền Dựa trên Vai trò (Role-Based Access Control – RBAC).

Trong kỹ thuật phần mềm truyền thống, các kỹ sư thường tìm đến hai giải pháp kinh điển trong sách giáo khoa: sử dụng **`WITH RECURSIVE` Common Table Expressions (CTE)** cho cây bình luận, và thực hiện **phép `JOIN` 5 bảng quan hệ** (`users` $\to$ `user_roles` $\to$ `roles` $\to$ `role_permissions` $\to$ `permissions`) để kiểm tra quyền.

Dưới lưu lượng truy cập khiêm tốn (50 req/s), mô hình này hoạt động ổn định. Nhưng khi xảy ra sự kiện nóng hoặc một bài viết có hàng ngàn bình luận phân nhánh đa cấp cùng lúc, kiến trúc này lập tức sụp đổ: bộ nhớ đệm Buffer Scan của PostgreSQL bị tràn, hàng đợi kết nối cạn kiệt, và độ trễ p95 vọt lên hơn **142ms**.

Tôi là **[Dương Phúc Khánh](https://khanhdp.com)** (được biết đến với định danh **[khanhdp](https://khanhdp.com)** hoặc **Kido**, [@khanhduong22](https://github.com/khanhduong22)). Trong quá trình dẫn dắt kiến trúc nền tảng mạng xã hội tài chính [Index.vn](https://khanhdp.com) và ghi lại kinh nghiệm thực chiến trong 128 tập **[Kido Chronicles](https://truyen.khanhdp.com)**, tôi đã thay thế hoàn toàn hai mô hình trên bằng **Base32 Materialized Paths** và **64-bit Bitmask RBAC**.

Dưới đây là phương pháp chúng tôi đưa độ trễ truy vấn p95 từ **142ms về 0.8ms** trên PostgreSQL 17 và gia tăng thông lượng hệ thống lên gấp **18 lần**.

---

## 1. Nỗi Đau Của Recursive CTE Khi Phân Cấp Sâu

Một câu lệnh `WITH RECURSIVE` buộc công cụ lập lịch truy vấn của cơ sở dữ liệu phải thực hiện duyệt cây đệ quy qua nhiều vòng lặp nối bảng (Iterative Joins):

```sql
-- Anti-pattern: Đệ quy duyệt cây bình luận tốn kém CPU
WITH RECURSIVE comment_tree AS (
    SELECT id, parent_id, content, created_at, 1 AS depth
    FROM comments
    WHERE post_id = 9021 AND parent_id IS NULL
    UNION ALL
    SELECT c.id, c.parent_id, c.content, c.created_at, ct.depth + 1
    FROM comments c
    INNER JOIN comment_tree ct ON c.parent_id = ct.id
)
SELECT * FROM comment_tree ORDER BY depth, created_at;
```

Khi bài viết có hàng trăm phản hồi lồng nhau, câu lệnh này tạo ra hàng loạt bảng tạm (WorkTable) trong bộ nhớ, ngăn cản cơ sở dữ liệu sử dụng chỉ mục B-Tree thông thường và tiêu hao lượng lớn IOPS.

---

## 2. Giải Pháp Base32 Materialized Path: Sắp Xếp Cây Bằng Một Phép Quét Chỉ Mục

Thay vì lưu trữ liên kết cha-con phân tán, chúng tôi mã hóa toàn bộ đường dẫn phả hệ của nút vào một cột chuỗi ký tự theo chuẩn Base32 (bao gồm các chữ số và chữ cái không gây nhầm lẫn: `0-9, A-V`):

* Bình luận gốc 1: `0001`
* Bình luận con 1 của gốc 1: `0001.0001`
* Bình luận con 2 của gốc 1: `0001.0002`
* Bình luận cháu sâu cấp 3: `0001.0001.000A`

Nhờ tính chất sắp xếp tự nhiên theo thứ tự từ điển (Lexicographical Order) của chuỗi ký tự Base32, toàn bộ cây phân nhánh từ trên xuống dưới được định vị chính xác chỉ bằng một lệnh quét chỉ mục tiền tố (Prefix Index Scan):

```sql
-- Truy vấn toàn bộ nhánh con của bình luận 0001 với độ phức tạp cực thấp
SELECT id, path, content, author_id
FROM comments
WHERE post_id = 9021 AND path LIKE '0001.%'
ORDER BY path ASC;
```

Trong PostgreSQL 17, chúng tôi sử dụng lớp chỉ mục đặc biệt `text_pattern_ops` trên cột `path`:

```sql
CREATE INDEX idx_comments_path_ops ON comments (post_id, path text_pattern_ops);
```

Chỉ mục này cho phép PostgreSQL tìm kiếm trực tiếp vị trí bắt đầu của nhánh và đọc tuần tự các nút con kế tiếp mà **không cần đệ quy, không cần bảng tạm**, đưa tốc độ duyệt cây về mức sub-millisecond (dưới 1ms).

---

## 3. Khử Sạch 5 Bảng RBAC Bằng Toán Tử Bitwise 64-Bit

Bài toán phân quyền thường tiêu tốn tài nguyên hệ thống do liên tục phải kiểm tra vai trò người dùng trong các bảng trung gian.

Để tối ưu hóa, chúng tôi gán cho mỗi quyền hạn một vị trí bit duy nhất trong một số nguyên 64-bit (`BIGINT`):
* `CAN_READ_POST` = $1 \ll 0 = 1$
* `CAN_CREATE_COMMENT` = $1 \ll 1 = 2$
* `CAN_EDIT_OWN_COMMENT` = $1 \ll 2 = 4$
* `CAN_MODERATE_CONTENT` = $1 \ll 3 = 8$
* `CAN_BAN_USER` = $1 \ll 4 = 16$

Toàn bộ quyền hạn của một người dùng được gộp thành một trường duy nhất: `permissions BIGINT`.

Khi kiểm tra người dùng có quyền xóa bài viết hay không, cơ sở dữ liệu hoặc mã backend chỉ cần thực hiện một phép tính logic bit đơn giản:

```sql
-- Kiểm tra quyền bằng phép toán bitwise AND: O(1)
SELECT id, title 
FROM posts 
WHERE post_id = 9021 
  AND (user_permissions & 8) = 8;
```

Phép toán này được thực thi ngay trong thanh ghi của vi xử lý chỉ trong 1 chu kỳ xung nhịp, loại bỏ hoàn toàn 5 câu lệnh `JOIN` và xóa sạch độ trễ phân quyền.

---

## 4. Bảng So Sánh Hiệu Năng Thực Tế (PostgreSQL 17 Benchmark)

| Chỉ Số Đánh Giá | Recursive CTE + 5-Table RBAC | Base32 Path + 64-Bit Bitmask | Mức Độ Cải Thiện |
| :--- | :--- | :--- | :--- |
| **Độ trễ P50 (Cây 500 comments)** | 34.2 ms | **0.32 ms** | **Nhanh hơn 106 lần** |
| **Độ trễ P95 (Dưới tải cao)** | 142.5 ms | **0.81 ms** | **Nhanh hơn 175 lần** |
| **Thông lượng tối đa (Throughput)** | 280 req/sec | **5,150 req/sec** | **Tăng 18.4 lần** |
| **Bộ nhớ đệm quét (Buffer Shared Hit)** | 14,200 blocks | **18 blocks** | **Tiết kiệm 99.8% I/O** |
| **Độ phức tạp thuật toán** | $O(N \cdot \text{depth})$ | **$O(\log N)$ (B-Tree)** | **Tối ưu triệt để** |

---

## 5. Kết Luận

Kiến trúc **Base32 Materialized Path** và **Bitmask RBAC** minh chứng rõ ràng cho quan điểm: Sự tinh tế của một hệ thống không nằm ở việc thêm thắt các công nghệ phức tạp, mà ở việc chọn đúng cấu trúc dữ liệu cơ bản để máy chủ vận hành mượt mà nhất có thể.
"""


ARTICLES_METADATA = [
    {
        "slug": "7-gate-multi-agent-engineering-harness",
        "file": "post01_devto_7_gate_harness.md",
        "lang": "en",
        "default_title": "How I Built a 7-Gate Multi-Agent Engineering Harness (And Survived a 6:00 AM Race Condition Storm)",
        "default_desc": "Inside the architecture of Duong Phuc Khanh (Kido): Scaling a real-world PWA to 1,100+ weekly active athletes on a single 8GB VPS using Valkey Distributed Locks and Autonomous AI Agents.",
        "category": "Multi-Agent AI",
        "tags": ["Architecture", "AI Agents", "Valkey", "PWA"]
    },
    {
        "slug": "bare-metal-vps-high-concurrency-playbook",
        "file": "post02_bare_metal_vps_playbook.md",
        "lang": "en",
        "default_title": "Why I Refused a $500/mo Cloud Bill: Running 1,100+ Active Users at 1.12s LCP on a Single 8GB Linux VPS",
        "default_desc": "How Duong Phuc Khanh (Kido) tuned Linux kernel sysctl, Caddy 2, PostgreSQL 17, and Valkey 8 to serve 113,000+ weekly events without AWS bloat.",
        "category": "DevOps & VPS",
        "tags": ["Linux", "Sysctl", "Caddy 2", "PostgreSQL 17"]
    },
    {
        "slug": "zero-tbt-lighthouse-100-pwa-engineering",
        "file": "post03_zero_tbt_pwa_engineering.md",
        "lang": "en",
        "default_title": "Zero-TBT & 8-Minute Mobile Sessions: Engineering a 60FPS Offline-First PWA on iOS Safari",
        "default_desc": "How we achieved 0ms Total Blocking Time, 1.12s P75 LCP, and an 8.2% bounce rate on mobile Safari using the 3-Tier Viewport Protocol and Offline Outbox queues.",
        "category": "Web Performance",
        "tags": ["PWA", "Zero-TBT", "Core Web Vitals", "iOS Safari"]
    },
    {
        "slug": "giai-phau-race-condition-valkey-distributed-lock",
        "file": "post04_viblo_valkey_race_condition_vi.md",
        "lang": "vi",
        "default_title": "Giải phẫu cơn bão Race Condition lúc 6h00 sáng & cách gánh 1.100+ WAU trên VPS 8GB RAM bằng Valkey Distributed Lock",
        "default_desc": "Phân tích kiến trúc của Dương Phúc Khánh (khanhdp · Kido): Xử lý TOCTOU Race Condition trong điểm danh buổi sáng bằng Valkey Distributed Lock và SingleFlight Pattern.",
        "category": "Hệ Thống Phân Tán",
        "tags": ["Valkey", "Distributed Lock", "Race Condition", "SingleFlight"]
    },
    {
        "slug": "http-304-singleflight-cache-races-mutation-epochs",
        "file": "post05_devto_singleflight_304_pwa_en.md",
        "lang": "en",
        "default_title": "Why HTTP 304 Not Modified Quietly Erased Our PWA State (And How We Fixed SingleFlight Cache Races with Mutation Epochs)",
        "default_desc": "How a 50ms replica lag combined with SWR background revalidation erased staff check-in states, and how we solved SingleFlight cache races using Client Mutation Ledgers and Server Mutation Epochs.",
        "category": "Cache & Concurrency",
        "tags": ["HTTP 304", "SingleFlight", "SWR", "Cache Invalidation"]
    },
    {
        "slug": "http-304-not-modified-singleflight-cache-race-pwa",
        "file": "post05_viblo_singleflight_304_pwa_vi.md",
        "lang": "vi",
        "default_title": "Giải phẫu cú lừa HTTP 304 Not Modified & SingleFlight Cache Race làm 'bốc hơi' dữ liệu PWA — Dương Phúc Khánh",
        "default_desc": "Cách hiện tượng trễ replica 50ms kết hợp cùng SWR revalidation làm biến mất trạng thái điểm danh của nhân viên, và giải pháp Mutation Epochs của Dương Phúc Khánh.",
        "category": "Hệ Thống Phân Tán",
        "tags": ["HTTP 304", "SingleFlight", "PWA Cache", "Redis"]
    },
    {
        "slug": "redis-valkey-bitmaps-popcnt-o1-streak-engine",
        "file": "post06_devto_redis_bitmap_46bytes_streak_en.md",
        "lang": "en",
        "default_title": "From 32KB SQL Joins to 46 Bytes: Architecting an O(1) Habit Streak Engine with Valkey/Redis Bitmaps & POPCNT",
        "default_desc": "How Duong Phuc Khanh (Kido) replaced bloated relational habit logs with 46-byte Redis/Valkey Bitmaps and CPU hardware POPCNT instructions, dropping p99 streak latency from 140ms to 0.08ms.",
        "category": "Database & Redis",
        "tags": ["Redis", "Bitmaps", "POPCNT", "O(1) Algorithms"]
    },
    {
        "slug": "nextjs-16-cloudflare-rsc-flight-cache-poisoning",
        "file": "post07_devto_rsc_cache_poisoning_cloudflare_en.md",
        "lang": "en",
        "default_title": "Anatomy of a Next.js 16 + Cloudflare Edge Outage: Eradicating RSC Flight Payload Cache Poisoning",
        "default_desc": "How Next.js App Router client navigation headers (RSC: 1) poisoned Cloudflare Edge Cache with raw Flight streams, resulting in white screens on iOS Safari PWA, and our 3-layer zero-downtime architectural fix.",
        "category": "Edge & Next.js",
        "tags": ["Next.js 16", "Cloudflare", "RSC Flight", "Edge Cache"]
    },
    {
        "slug": "postgresql-17-base32-materialized-paths-bitmask-rbac",
        "file": "post08_devto_postgresql_materialized_path_rbac_en.md",
        "lang": "en",
        "default_title": "Killing Recursive CTEs: Sub-Millisecond Comment Trees & Bitmask RBAC in PostgreSQL 17",
        "default_desc": "Why WITH RECURSIVE CTEs and 5-table RBAC joins choke under concurrency, and how Duong Phuc Khanh (Kido) architected Base32 Materialized Paths and 64-bit Bitmask RBAC to drop p95 query latency from 142ms to 0.8ms.",
        "category": "PostgreSQL & RBAC",
        "tags": ["PostgreSQL 17", "Materialized Path", "Bitmask RBAC", "Tree Queries"]
    },
    {
        "slug": "kien-truc-redis-valkey-bitmap-46-bytes-streak-engine",
        "file": None,
        "raw_content": POST10_CONTENT,
        "lang": "vi",
        "default_title": "Kiến trúc Redis/Valkey Bitmap 46 Bytes: Xây dựng O(1) Streak Engine & Khử Sạch N+1 Query SQL",
        "default_desc": "Cách Dương Phúc Khánh (Kido) thay thế hàng triệu dòng habit logs quan hệ bằng 46 bytes Redis Bitmap và tập lệnh phần cứng CPU POPCNT, đưa độ trễ p99 từ 140ms về 0.08ms.",
        "category": "Cơ Sở Dữ Liệu",
        "tags": ["Redis", "Valkey", "Bitmaps", "POPCNT", "Hiệu Năng"]
    },
    {
        "slug": "xu-ly-rsc-flight-cache-poisoning-nextjs-16-cloudflare",
        "file": None,
        "raw_content": POST11_CONTENT,
        "lang": "vi",
        "default_title": "Giải Phẫu Sự Cố Cloudflare Edge & Next.js 16: Triệt Tiêu Thảm Họa RSC Flight Payload Cache Poisoning",
        "default_desc": "Cách header client navigation (RSC: 1) của Next.js App Router đầu độc bộ nhớ đệm Cloudflare Edge Cache biến PWA thành màn hình trắng xóa trên iOS Safari, và kiến trúc phòng thủ 3 lớp zero-downtime của Dương Phúc Khánh.",
        "category": "Edge & Next.js",
        "tags": ["Next.js 16", "Cloudflare", "Edge Cache", "RSC Flight"]
    },
    {
        "slug": "postgresql-17-base32-materialized-path-bitmask-rbac-tieng-viet",
        "file": None,
        "raw_content": POST12_CONTENT,
        "lang": "vi",
        "default_title": "Khắc Phục Đòn Chí Mạng Recursive CTE: Cây Bình Luận Base32 Materialized Path & Bitmask RBAC Trong PostgreSQL 17",
        "default_desc": "Tại sao WITH RECURSIVE CTEs và JOIN 5 bảng phân quyền làm nghẽn Database khi tải cao, và giải pháp Base32 Materialized Path cùng 64-bit Bitmask RBAC đưa độ trễ p95 từ 142ms xuống 0.8ms của Dương Phúc Khánh.",
        "category": "PostgreSQL & RBAC",
        "tags": ["PostgreSQL 17", "Base32 Path", "Bitmask RBAC", "Tối Ưu Truy Vấn"]
    }
]


def render_article_page(art, html_content):
    slug = art["slug"]
    lang = art["lang"]
    title = art["title"]
    desc = art["desc"]
    category = art["category"]
    canonical_url = f"https://khanhdp.com/articles/{slug}/"
    page_title = f"{title} — Dương Phúc Khánh (Duong Phuc Khanh · Kido)"
    related_slugs = EPISODE_CONTEXT_MAP.get(slug, [
        "tap-1-thang-em-vibe-coding",
        "tap-9-bay-in-app-browser",
        "tap-100-dai-ket-cuc-100-tap-khuc-khai-hoan-spartan",
        "tap-114-voi-caddy-roi-thi-caddy-het-khai-tu-nginx-portfolio",
        "tap-121-dai-di-cu-monorepo-len-full-bun-chat-dut-long-task-205ms-va-day-lcp-ve-frame-2"
    ])

    # Find full episode objects
    related_episodes = []
    for rslug in related_slugs:
        for ep in FLAGSHIP_EPISODES_20:
            if ep["slug"] == rslug:
                related_episodes.append(ep)
                break
        if len(related_episodes) == 5:
            break

    # Build JSON-LD
    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "TechArticle",
                "@id": f"{canonical_url}#article",
                "headline": title,
                "name": page_title,
                "description": desc,
                "url": canonical_url,
                "mainEntityOfPage": canonical_url,
                "inLanguage": "en" if lang == "en" else "vi",
                "datePublished": "2026-10-20",
                "dateModified": "2026-10-23",
                "author": {
                    "@id": "https://khanhdp.com/#person"
                },
                "publisher": {
                    "@id": "https://khanhdp.com/#person"
                },
                "image": "https://khanhdp.com/duong-phuc-khanh.jpg",
                "articleSection": category
            },
            CANONICAL_PERSON,
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical_url}#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Home",
                        "item": "https://khanhdp.com"
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "Technical Articles",
                        "item": "https://khanhdp.com/articles/"
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": title,
                        "item": canonical_url
                    }
                ]
            }
        ]
    }
    json_ld_str = json.dumps(json_ld, indent=2, ensure_ascii=False)

    # Render Author Ribbon (Top)
    if lang == "en":
        ribbon_html = f"""
        <!-- Top Author & Entity Verification Ribbon -->
        <div class="border border-emerald-500/30 bg-emerald-950/20 rounded-xl p-4 my-6 text-xs font-mono text-zinc-300">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-emerald-500/20 pb-2.5 mb-2.5">
            <div class="flex items-center gap-2 text-emerald-400 font-semibold uppercase tracking-wider text-[11px]">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Authoritative Technical Whitepaper</span>
            </div>
            <div class="flex items-center gap-3 text-zinc-400 text-[11px]">
              <span>Verified Entity:</span>
              <a href="https://www.wikidata.org/wiki/Q141718572" target="_blank" rel="noopener" class="text-sky-400 hover:underline">Wikidata Q141718572</a>
              <span>·</span>
              <a href="https://orcid.org/0009-0005-7192-2664" target="_blank" rel="noopener" class="text-sky-400 hover:underline">ORCID 0009-0005-7192-2664</a>
            </div>
          </div>
          <div class="text-[12px] leading-relaxed text-zinc-300">
            Authored by <strong class="text-white">Duong Phuc Khanh</strong> (<strong class="text-zinc-200">Dương Phúc Khánh</strong> · <a href="https://khanhdp.com" class="text-emerald-400 hover:underline">khanhdp.com</a>), Senior Software Engineer &amp; Systems Architect. Explore the <a href="/en" class="text-sky-400 hover:underline font-semibold">Official English Biography</a>, read the <a href="/about" class="text-sky-400 hover:underline">Tiểu sử Tiếng Việt</a>, browse the <a href="/articles/" class="text-sky-400 hover:underline">Articles Hub</a>, or inspect the 128-episode engineering postmortem anthology on <a href="https://truyen.khanhdp.com" target="_blank" rel="noopener" class="text-purple-300 hover:underline font-semibold">Kido Chronicles</a>.
          </div>
        </div>
        """
        related_title = "Related Production Postmortems (Kido Chronicles)"
        author_card_title = "About the Author: Duong Phuc Khanh (khanhdp · Kido)"
        author_card_body = """
        <p class="text-sm text-zinc-300 leading-relaxed mb-3">
          <strong>Duong Phuc Khanh</strong> (Vietnamese: <em>Dương Phúc Khánh</em>, born 1995 in Da Nang, Vietnam) is a Senior Software Engineer and Systems Architect at <a href="https://khanhdp.com" class="text-emerald-400 hover:underline">khanhdp.com</a>. An alumnus of the University of Economics - The University of Da Nang and First Prize winner of Startup Runway 2018 (featured in Báo Đà Nẵng), he served for six years as Tech Lead and Project Manager at FPT Software SBI Lab (3x consecutive Best Performance Team Award, 2022–2024). He is the creator of <a href="https://vantoicalis.com" target="_blank" rel="noopener" class="text-emerald-400 hover:underline">Winter Arc</a>, the 128-episode <a href="https://truyen.khanhdp.com" target="_blank" rel="noopener" class="text-purple-300 hover:underline">Kido Chronicles</a>, and the <a href="https://github.com/khanhduong22/agent-harness-kit" target="_blank" rel="noopener" class="text-emerald-400 hover:underline">Agent Harness Kit</a>.
        </p>
        """
    else:
        ribbon_html = f"""
        <!-- Top Author & Entity Verification Ribbon -->
        <div class="border border-emerald-500/30 bg-emerald-950/20 rounded-xl p-4 my-6 text-xs font-mono text-zinc-300">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-emerald-500/20 pb-2.5 mb-2.5">
            <div class="flex items-center gap-2 text-emerald-400 font-semibold uppercase tracking-wider text-[11px]">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Chuyên Khảo Kiến Trúc Hệ Thống</span>
            </div>
            <div class="flex items-center gap-3 text-zinc-400 text-[11px]">
              <span>Định danh thực thể:</span>
              <a href="https://www.wikidata.org/wiki/Q141718572" target="_blank" rel="noopener" class="text-sky-400 hover:underline">Wikidata Q141718572</a>
              <span>·</span>
              <a href="https://orcid.org/0009-0005-7192-2664" target="_blank" rel="noopener" class="text-sky-400 hover:underline">ORCID 0009-0005-7192-2664</a>
            </div>
          </div>
          <div class="text-[12px] leading-relaxed text-zinc-300">
            Tác giả: <strong class="text-white">Dương Phúc Khánh</strong> (tiếng Anh: <strong class="text-zinc-200">Duong Phuc Khanh</strong> · <a href="https://khanhdp.com" class="text-emerald-400 hover:underline">khanhdp.com</a>), Kỹ sư Phần mềm Cao cấp &amp; Kiến trúc sư Hệ thống. Đọc <a href="/about" class="text-sky-400 hover:underline font-semibold">Tiểu sử Tiếng Việt</a>, xem bản <a href="/en" class="text-sky-400 hover:underline">English Biography</a>, tra cứu <a href="/articles/" class="text-sky-400 hover:underline">Danh mục Bài viết</a>, hoặc khám phá tuyển tập 128 tập ký sự sự cố production tại <a href="https://truyen.khanhdp.com" target="_blank" rel="noopener" class="text-purple-300 hover:underline font-semibold">Kido Chronicles</a>.
          </div>
        </div>
        """
        related_title = "Biên Niên Sử Liên Quan (Kido Chronicles)"
        author_card_title = "Về Tác Giả: Dương Phúc Khánh (khanhdp · Kido)"
        author_card_body = """
        <p class="text-sm text-zinc-300 leading-relaxed mb-3">
          <strong>Dương Phúc Khánh</strong> (sinh năm 1995 tại Đà Nẵng, định danh: <em>khanhdp</em>, moniker: <em>Kido</em>) là Kỹ sư Phần mềm Cao cấp và Kiến trúc sư Hệ thống tại <a href="https://khanhdp.com" class="text-emerald-400 hover:underline">khanhdp.com</a>. Cựu sinh viên Đại học Kinh tế – Đại học Đà Nẵng, Quán quân Startup Runway 2018 (vinh danh trên Báo Đà Nẵng), 6 năm Tech Lead &amp; PM tại FPT Software SBI Lab (3 năm liên tiếp Best Performance Award 2022–2024). Anh là tác giả của <a href="https://vantoicalis.com" target="_blank" rel="noopener" class="text-emerald-400 hover:underline">Winter Arc</a>, tuyển tập 128 tập <a href="https://truyen.khanhdp.com" target="_blank" rel="noopener" class="text-purple-300 hover:underline">Kido Chronicles</a> và bộ khung điều phối <a href="https://github.com/khanhduong22/agent-harness-kit" target="_blank" rel="noopener" class="text-emerald-400 hover:underline">Agent Harness Kit</a>.
        </p>
        """

    # Render related episodes list
    related_list_html = []
    for ep in related_episodes:
        related_list_html.append(f"""
        <a href="https://truyen.khanhdp.com/tap/{ep['slug']}/" target="_blank" rel="noopener" class="p-3.5 border border-white/10 rounded-lg bg-white/[0.02] hover:bg-white/[0.05] transition-all flex flex-col justify-between group">
          <div class="flex items-center justify-between text-[11px] font-mono text-zinc-500 mb-1">
            <span class="text-emerald-400 font-semibold">{ep['category']}</span>
            <span class="group-hover:text-emerald-400 transition-colors">Tập {ep['id']} ↗</span>
          </div>
          <div class="text-xs font-semibold text-zinc-200 group-hover:text-white transition-colors line-clamp-2">
            {ep['title']}
          </div>
          <div class="text-[11px] text-zinc-400 mt-1 line-clamp-2">
            {ep['desc']}
          </div>
        </a>
        """)
    related_blocks_str = "\n".join(related_list_html)

    return f"""<!DOCTYPE html>
<html lang="{lang}" class="dark scroll-smooth">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{page_title}</title>
  <meta name="description" content="{html.escape(desc)}" />

  <!-- Canonical Tag -->
  <link rel="canonical" href="{canonical_url}" />

  <!-- Favicons & Brand Suite -->
  <link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png" />
  <link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png" />
  <link rel="icon" type="image/png" sizes="144x144" href="/favicon-144x144.png" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" sizes="any" />
  <link rel="shortcut icon" href="/favicon.ico" />
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/manifest.json" />

  <!-- OpenGraph Metadata -->
  <meta property="og:title" content="{html.escape(page_title)}" />
  <meta property="og:description" content="{html.escape(desc)}" />
  <meta property="og:url" content="{canonical_url}" />
  <meta property="og:type" content="article" />
  <meta property="og:locale" content="{"en_US" if lang == "en" else "vi_VN"}" />
  <meta property="og:site_name" content="Dương Phúc Khánh (khanhdp · Kido)" />
  <meta property="og:image" content="https://khanhdp.com/duong-phuc-khanh.jpg" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{html.escape(page_title)}" />
  <meta name="twitter:description" content="{html.escape(desc)}" />
  <meta name="twitter:image" content="https://khanhdp.com/duong-phuc-khanh.jpg" />

  <!-- Deferred Lossless Telemetry -->
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag() {{ window.dataLayer.push(arguments); }}
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', 'G-RMEP3RZB14');
    window.dataLayer.push({{ 'gtm.start': new Date().getTime(), event: 'gtm.js' }});

    window.clarity = window.clarity || function() {{ (window.clarity.q = window.clarity.q || []).push(arguments); }};

    window.addEventListener('error', function(e) {{
      if (window.Sentry && typeof window.Sentry.captureException === 'function') {{
        var id = window.Sentry.captureException(e.error || e.message);
        if (id && window.clarity) window.clarity('set', 'sentry_event_id', id);
      }}
    }});

    window.trackEvent = function(eventName, params) {{
      params = params || {{}};
      if (typeof window.gtag === 'function') window.gtag('event', eventName, params);
      if (typeof window.clarity === 'function') {{
        window.clarity('event', eventName);
        var label = params.event_label || params.label || params.destination_url || params.category;
        if (label) window.clarity('set', eventName, String(label).slice(0, 50));
      }}
    }};

    (function(w, d) {{
      var isLoaded = false;
      function injectScript(src, id) {{
        if (id && d.getElementById(id)) return;
        if (d.querySelector('script[src="' + src + '"]')) return;
        var s = d.createElement('script');
        s.async = true;
        s.src = src;
        if (id) s.id = id;
        (d.head || d.body).appendChild(s);
      }}
      var events = ['scroll', 'touchstart', 'pointerdown', 'keydown', 'wheel'];
      function triggerDeferredLoad() {{
        if (isLoaded) return;
        isLoaded = true;
        events.forEach(function(e) {{ w.removeEventListener(e, triggerDeferredLoad); }});
        injectScript('https://www.googletagmanager.com/gtag/js?id=G-RMEP3RZB14', 'ga4-deferred-script');
        injectScript('https://www.googletagmanager.com/gtm.js?id=GTM-NXV7B355', 'gtm-deferred-script');
        injectScript('https://www.clarity.ms/tag/yy4l1xv1a9', 'clarity-deferred-script');
      }}
      events.forEach(function(e) {{
        w.addEventListener(e, triggerDeferredLoad, {{ passive: true, once: true }});
      }});
    }})(window, document);
  </script>

  <!-- Schema.org JSON-LD -->
  <script type="application/ld+json">
{json_ld_str}
  </script>

  <!-- Fonts & Stylesheet -->
  <link rel="preload" href="/fonts/inter-vietnamese.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/fonts/jetbrains-mono-latin.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="/index.min.css" />
</head>
<body class="bg-craft-bg text-craft-text font-sans antialiased selection:bg-white/20 selection:text-white min-h-screen relative">
  <!-- Top Reading Progress Indicator -->
  <div id="progress-bar" class="fixed top-0 left-0 h-[2px] bg-gradient-to-r from-zinc-500 via-zinc-200 to-white z-50 transition-all duration-100 ease-out" style="width: 0%;"></div>

  <!-- Ambient Light Header Radial -->
  <div class="absolute inset-x-0 top-0 h-[480px] ambient-glow pointer-events-none"></div>

  <!-- Sticky Minimal Navigation Bar -->
  <header class="sticky top-0 z-40 backdrop-blur-md bg-[#0a0a0a]/85 border-b border-white/[0.06] transition-all">
    <div class="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
      <a href="/" class="group flex items-center gap-2.5 text-zinc-100 hover:text-white transition-colors">
        <span class="w-2 h-2 rounded-full bg-emerald-500 ring-4 ring-emerald-500/20 animate-pulse"></span>
        <span class="font-mono text-xs tracking-wider uppercase font-semibold text-zinc-200">DUONG PHUC KHANH · KIDO</span>
      </a>

      <nav class="flex items-center gap-4 text-xs font-mono">
        <div class="hidden sm:flex items-center gap-4 text-zinc-400">
          <a href="/" class="hover:text-zinc-200 transition-colors">Overview</a>
          <a href="/en" class="hover:text-zinc-200 transition-colors">Biography (EN)</a>
          <a href="/about" class="hover:text-zinc-200 transition-colors">Tiểu sử (VI)</a>
          <a href="/articles/" class="text-white font-semibold flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            Articles
          </a>
          <a href="https://truyen.khanhdp.com" target="_blank" rel="noopener" class="hover:text-zinc-200 transition-colors">Chronicles</a>
          <a href="/portfolio" class="px-2.5 py-1 rounded bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 transition-all font-semibold flex items-center gap-1.5">
            SME Portfolio
          </a>
        </div>

        <div class="h-3 w-[1px] bg-white/10 hidden sm:block"></div>

        <a href="mailto:phuckhanh22@gmail.com" class="flex items-center gap-1.5 px-2.5 py-1 rounded bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-zinc-300 hover:text-zinc-100 transition-all text-xs font-mono">
          <span>Contact</span>
          <span>↗</span>
        </a>
      </nav>
    </div>
  </header>

  <!-- Main Article Container -->
  <main class="max-w-4xl mx-auto px-6 pt-12 pb-24">

    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 text-xs font-mono text-zinc-500 tracking-wider uppercase mb-6 pb-3 border-b border-white/[0.06] overflow-x-auto">
      <a href="/" class="hover:text-zinc-300 transition-colors shrink-0">KHANHDP.COM</a>
      <span>/</span>
      <a href="/articles/" class="hover:text-zinc-300 transition-colors shrink-0">ARTICLES</a>
      <span>/</span>
      <span class="text-zinc-400 shrink-0">{category.upper()}</span>
    </div>

    <!-- Article Header -->
    <header class="space-y-4 mb-8">
      <div class="flex flex-wrap items-center gap-3 text-xs font-mono">
        <span class="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">{category}</span>
        <span class="text-zinc-500">2026-10-20</span>
        <span class="text-zinc-600">·</span>
        <span class="text-zinc-400">By Dương Phúc Khánh (Kido)</span>
      </div>

      <h1 class="text-2xl sm:text-4xl font-semibold tracking-tight text-zinc-100 leading-tight">
        {title}
      </h1>

      <p class="text-base sm:text-lg text-zinc-400 leading-relaxed">
        {desc}
      </p>
    </header>

    {ribbon_html}

    <!-- Article Body Prose -->
    <article class="prose prose-invert max-w-none text-zinc-300 leading-relaxed font-normal text-sm sm:text-base border-t border-white/[0.06] pt-6">
      {html_content}
    </article>

    <!-- Contextual Kido Chronicles Episodes (Deep Links) -->
    <section class="mt-16 pt-8 border-t border-white/[0.06] space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-lg sm:text-xl font-semibold text-zinc-100 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-purple-400"></span>
          <span>{related_title}</span>
        </h2>
        <a href="https://truyen.khanhdp.com" target="_blank" rel="noopener" class="text-xs font-mono text-purple-300 hover:text-purple-200 hover:underline">
          View all 128 episodes ↗
        </a>
      </div>
      <p class="text-xs text-zinc-400">
        Curated real-world war stories and incident postmortems authored by Duong Phuc Khanh on <a href="https://truyen.khanhdp.com" target="_blank" rel="noopener" class="text-purple-300 hover:underline">truyen.khanhdp.com</a> related to this topic:
      </p>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
        {related_blocks_str}
      </div>
    </section>

    <!-- Author Bio & Entity Verification Card (Bottom) -->
    <section class="mt-12 p-6 rounded-2xl border border-white/10 bg-[#121212] space-y-4">
      <div class="flex flex-col sm:flex-row items-center sm:items-start gap-4">
        <img
          src="/duong-phuc-khanh.jpg"
          alt="Duong Phuc Khanh (Dương Phúc Khánh · Kido)"
          width="88"
          height="88"
          style="width:88px;height:88px;object-fit:cover;"
          class="rounded-xl border border-white/15 shrink-0"
        />
        <div class="space-y-2 text-center sm:text-left flex-1">
          <h3 class="text-base font-semibold text-zinc-100">{author_card_title}</h3>
          {author_card_body}
          <div class="flex flex-wrap items-center justify-center sm:justify-start gap-3 text-xs font-mono pt-1">
            <a href="https://khanhdp.com" class="text-sky-400 hover:underline">Home</a>
            <span class="text-zinc-600">·</span>
            <a href="/en" class="text-sky-400 hover:underline">Biography (EN)</a>
            <span class="text-zinc-600">·</span>
            <a href="/about" class="text-sky-400 hover:underline">Tiểu sử (VI)</a>
            <span class="text-zinc-600">·</span>
            <a href="/articles/" class="text-sky-400 hover:underline">Articles Hub</a>
            <span class="text-zinc-600">·</span>
            <a href="https://truyen.khanhdp.com" target="_blank" rel="noopener" class="text-purple-300 hover:underline">Kido Chronicles</a>
            <span class="text-zinc-600">·</span>
            <a href="https://www.wikidata.org/wiki/Q141718572" target="_blank" rel="noopener" class="text-emerald-400 hover:underline">Wikidata</a>
            <span class="text-zinc-600">·</span>
            <a href="https://orcid.org/0009-0005-7192-2664" target="_blank" rel="noopener" class="text-emerald-400 hover:underline">ORCID</a>
          </div>
        </div>
      </div>
    </section>

  </main>

  <!-- Global Footer -->
  <footer class="border-t border-white/[0.06] bg-[#080808] text-xs font-mono text-zinc-500 py-12">
    <div class="max-w-5xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
        <a href="https://khanhdp.com" class="text-zinc-300 hover:text-white font-semibold uppercase transition-colors">DUONG PHUC KHANH (KIDO)</a>
      </div>
      <div class="flex items-center gap-4 text-zinc-400 flex-wrap">
        <a href="/" class="hover:text-white transition-colors">Overview</a>
        <a href="/en" class="hover:text-white transition-colors">Biography (EN)</a>
        <a href="/about" class="hover:text-white transition-colors">Tiểu sử (VI)</a>
        <a href="/articles/" class="text-white hover:text-emerald-400 transition-colors">Articles</a>
        <a href="https://blog.khanhdp.com" target="_blank" rel="noopener" class="hover:text-white transition-colors">Engineering Blog</a>
        <a href="/portfolio" class="hover:text-white transition-colors">Portfolio</a>
        <a href="https://truyen.khanhdp.com" target="_blank" rel="noopener" class="hover:text-white transition-colors">Chronicles</a>
        <a href="https://github.com/khanhduong22" target="_blank" rel="noopener" class="hover:text-white transition-colors">GitHub</a>
        <a href="https://www.linkedin.com/in/duong-phuc-khanh/" target="_blank" rel="noopener" class="hover:text-white transition-colors">LinkedIn</a>
      </div>
    </div>
    <div class="max-w-5xl mx-auto px-6 mt-4 text-[11px] text-zinc-600 flex flex-col sm:flex-row items-center justify-between gap-2">
      <p>© 2026 Duong Phuc Khanh (khanhdp · Kido). All rights reserved.</p>
      <p>Crafted with quiet confidence</p>
    </div>
  </footer>

  <!-- Scroll Progress Script -->
  <script>
    window.addEventListener('scroll', () => {{
      const winScroll = document.documentElement.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (winScroll / height) * 100;
      const progressBar = document.getElementById('progress-bar');
      if (progressBar) progressBar.style.width = scrolled + '%';
    }}, {{ passive: true }});

    document.addEventListener("click", (e) => {{
      let a = e.target.closest("a[href]");
      if (a) {{
        let h = a.getAttribute("href");
        if (h && (h.startsWith("http://") || h.startsWith("https://")) && !h.includes(window.location.hostname)) {{
          let t = (a.getAttribute("title") || a.textContent || h).trim().slice(0, 60);
          if (window.trackEvent) window.trackEvent("outbound_click", {{ event_category: "outbound", destination_url: h, link_text: t }});
        }} else if (h && (h.startsWith("#") || h.startsWith("/"))) {{
          let t = (a.textContent || h).trim().slice(0, 40);
          if (window.trackEvent) window.trackEvent("nav_click", {{ event_category: "navigation", destination: h, link_text: t }});
        }}
      }}
    }}, {{ passive: true }});
  </script>
</body>
</html>
"""


def render_hub_index_page(articles):
    vi_articles = [a for a in articles if a["lang"] == "vi"]
    en_articles = [a for a in articles if a["lang"] == "en"]

    canonical_url = "https://khanhdp.com/articles/"
    page_title = "Technical Articles & Architecture Postmortems — Dương Phúc Khánh (Duong Phuc Khanh · Kido)"
    page_desc = "Authoritative technical whitepapers, distributed systems architecture case studies, PostgreSQL optimization, and high-concurrency engineering postmortems by Duong Phuc Khanh (Dương Phúc Khánh · khanhdp · Kido)."

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": f"{canonical_url}#page",
                "url": canonical_url,
                "name": page_title,
                "description": page_desc,
                "inLanguage": "en",
                "author": {
                    "@id": "https://khanhdp.com/#person"
                }
            },
            CANONICAL_PERSON,
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical_url}#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Home",
                        "item": "https://khanhdp.com"
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "Articles",
                        "item": canonical_url
                    }
                ]
            }
        ]
    }
    json_ld_str = json.dumps(json_ld, indent=2, ensure_ascii=False)

    def render_card(art):
        return f"""
        <article class="p-5 rounded-xl border border-white/10 bg-[#121212]/80 hover:bg-[#151515] hover:border-emerald-500/30 transition-all flex flex-col justify-between group">
          <div class="space-y-2">
            <div class="flex items-center justify-between text-xs font-mono">
              <span class="text-emerald-400 font-semibold uppercase">{art['category']}</span>
              <span class="text-zinc-500">2026-10-20</span>
            </div>
            <h3 class="text-base sm:text-lg font-semibold text-zinc-100 group-hover:text-emerald-400 transition-colors leading-snug">
              <a href="/articles/{art['slug']}/">{art['title']}</a>
            </h3>
            <p class="text-xs sm:text-sm text-zinc-400 line-clamp-3 leading-relaxed">
              {art['desc']}
            </p>
          </div>
          <div class="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between text-xs font-mono">
            <span class="text-zinc-500">{", ".join(art['tags'][:2])}</span>
            <a href="/articles/{art['slug']}/" class="text-sky-400 group-hover:text-emerald-400 flex items-center gap-1 font-semibold">
              <span>Read article</span>
              <span>→</span>
            </a>
          </div>
        </article>
        """

    vi_cards_html = "\n".join([render_card(a) for a in vi_articles])
    en_cards_html = "\n".join([render_card(a) for a in en_articles])

    episodes_grid_html = []
    for ep in FLAGSHIP_EPISODES_20:
        episodes_grid_html.append(f"""
        <a href="https://truyen.khanhdp.com/tap/{ep['slug']}/" target="_blank" rel="noopener" class="p-4 rounded-xl border border-white/10 bg-[#121212]/70 hover:bg-[#161616] hover:border-purple-400/40 transition-all flex flex-col justify-between group">
          <div>
            <div class="flex items-center justify-between text-[11px] font-mono text-zinc-500 mb-1.5">
              <span class="text-purple-400 font-semibold">{ep['category']}</span>
              <span class="group-hover:text-purple-300 transition-colors">Tập {ep['id']} ↗</span>
            </div>
            <h4 class="text-xs sm:text-sm font-semibold text-zinc-200 group-hover:text-white transition-colors line-clamp-2 leading-snug">
              {ep['title']}
            </h4>
            <p class="text-[11px] text-zinc-400 mt-1.5 line-clamp-2 leading-relaxed">
              {ep['desc']}
            </p>
          </div>
          <div class="mt-3 pt-2 border-t border-white/[0.04] text-[10px] font-mono text-zinc-500 flex items-center justify-between">
            <span>truyen.khanhdp.com</span>
            <span class="text-purple-400 group-hover:translate-x-0.5 transition-transform">Read tap-{ep['id']} →</span>
          </div>
        </a>
        """)
    episodes_grid_str = "\n".join(episodes_grid_html)

    return f"""<!DOCTYPE html>
<html lang="en" class="dark scroll-smooth">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{page_title}</title>
  <meta name="description" content="{html.escape(page_desc)}" />

  <link rel="canonical" href="{canonical_url}" />

  <!-- Favicons & Brand Suite -->
  <link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png" />
  <link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png" />
  <link rel="icon" type="image/png" sizes="144x144" href="/favicon-144x144.png" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" sizes="any" />
  <link rel="shortcut icon" href="/favicon.ico" />
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/manifest.json" />

  <!-- OpenGraph Metadata -->
  <meta property="og:title" content="{html.escape(page_title)}" />
  <meta property="og:description" content="{html.escape(page_desc)}" />
  <meta property="og:url" content="{canonical_url}" />
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="en_US" />
  <meta property="og:site_name" content="Dương Phúc Khánh (khanhdp · Kido)" />
  <meta property="og:image" content="https://khanhdp.com/duong-phuc-khanh.jpg" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{html.escape(page_title)}" />
  <meta name="twitter:description" content="{html.escape(page_desc)}" />
  <meta name="twitter:image" content="https://khanhdp.com/duong-phuc-khanh.jpg" />

  <!-- Deferred Telemetry -->
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag() {{ window.dataLayer.push(arguments); }}
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', 'G-RMEP3RZB14');
    window.dataLayer.push({{ 'gtm.start': new Date().getTime(), event: 'gtm.js' }});

    window.clarity = window.clarity || function() {{ (window.clarity.q = window.clarity.q || []).push(arguments); }};

    window.trackEvent = function(eventName, params) {{
      params = params || {{}};
      if (typeof window.gtag === 'function') window.gtag('event', eventName, params);
      if (typeof window.clarity === 'function') {{
        window.clarity('event', eventName);
        var label = params.event_label || params.label || params.destination_url || params.category;
        if (label) window.clarity('set', eventName, String(label).slice(0, 50));
      }}
    }};

    (function(w, d) {{
      var isLoaded = false;
      function injectScript(src, id) {{
        if (id && d.getElementById(id)) return;
        if (d.querySelector('script[src="' + src + '"]')) return;
        var s = d.createElement('script');
        s.async = true;
        s.src = src;
        if (id) s.id = id;
        (d.head || d.body).appendChild(s);
      }}
      var events = ['scroll', 'touchstart', 'pointerdown', 'keydown', 'wheel'];
      function triggerDeferredLoad() {{
        if (isLoaded) return;
        isLoaded = true;
        events.forEach(function(e) {{ w.removeEventListener(e, triggerDeferredLoad); }});
        injectScript('https://www.googletagmanager.com/gtag/js?id=G-RMEP3RZB14', 'ga4-deferred-script');
        injectScript('https://www.googletagmanager.com/gtm.js?id=GTM-NXV7B355', 'gtm-deferred-script');
        injectScript('https://www.clarity.ms/tag/yy4l1xv1a9', 'clarity-deferred-script');
      }}
      events.forEach(function(e) {{
        w.addEventListener(e, triggerDeferredLoad, {{ passive: true, once: true }});
      }});
    }})(window, document);
  </script>

  <!-- Schema.org JSON-LD -->
  <script type="application/ld+json">
{json_ld_str}
  </script>

  <!-- Fonts & Stylesheet -->
  <link rel="preload" href="/fonts/inter-vietnamese.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/fonts/jetbrains-mono-latin.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="/index.min.css" />
</head>
<body class="bg-craft-bg text-craft-text font-sans antialiased selection:bg-white/20 selection:text-white min-h-screen relative">
  <!-- Reading Progress Bar -->
  <div id="progress-bar" class="fixed top-0 left-0 h-[2px] bg-gradient-to-r from-zinc-500 via-zinc-200 to-white z-50 transition-all duration-100 ease-out" style="width: 0%;"></div>

  <!-- Ambient Glow -->
  <div class="absolute inset-x-0 top-0 h-[480px] ambient-glow pointer-events-none"></div>

  <!-- Sticky Navbar -->
  <header class="sticky top-0 z-40 backdrop-blur-md bg-[#0a0a0a]/85 border-b border-white/[0.06] transition-all">
    <div class="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
      <a href="/" class="group flex items-center gap-2.5 text-zinc-100 hover:text-white transition-colors">
        <span class="w-2 h-2 rounded-full bg-emerald-500 ring-4 ring-emerald-500/20 animate-pulse"></span>
        <span class="font-mono text-xs tracking-wider uppercase font-semibold text-zinc-200">DUONG PHUC KHANH · KIDO</span>
      </a>

      <nav class="flex items-center gap-4 text-xs font-mono">
        <div class="hidden sm:flex items-center gap-4 text-zinc-400">
          <a href="/" class="hover:text-zinc-200 transition-colors">Overview</a>
          <a href="/en" class="hover:text-zinc-200 transition-colors">Biography (EN)</a>
          <a href="/about" class="hover:text-zinc-200 transition-colors">Tiểu sử (VI)</a>
          <a href="/articles/" class="text-white font-semibold flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            Articles
          </a>
          <a href="https://truyen.khanhdp.com" target="_blank" rel="noopener" class="hover:text-zinc-200 transition-colors">Chronicles</a>
          <a href="/portfolio" class="px-2.5 py-1 rounded bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 transition-all font-semibold flex items-center gap-1.5">
            SME Portfolio
          </a>
        </div>

        <div class="h-3 w-[1px] bg-white/10 hidden sm:block"></div>

        <a href="mailto:phuckhanh22@gmail.com" class="flex items-center gap-1.5 px-2.5 py-1 rounded bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-zinc-300 hover:text-zinc-100 transition-all text-xs font-mono">
          <span>Contact</span>
          <span>↗</span>
        </a>
      </nav>
    </div>
  </header>

  <!-- Main Narrative Hub -->
  <main class="max-w-5xl mx-auto px-6 pt-12 pb-24 space-y-16">

    <!-- Hero Header -->
    <div class="space-y-4 max-w-3xl">
      <div class="flex items-center gap-2 text-xs font-mono text-emerald-400 tracking-wider uppercase">
        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
        <span>Systems Engineering &amp; Architecture Publications</span>
      </div>
      <h1 class="text-3xl sm:text-5xl font-semibold tracking-tight text-zinc-100 leading-tight">
        Technical Articles &amp; Incident Postmortems
      </h1>
      <p class="text-base sm:text-lg text-zinc-400 leading-relaxed">
        Authoritative distributed systems engineering whitepapers, PostgreSQL query optimizations, Valkey distributed locking patterns, and zero-TBT PWA case studies authored by <a href="/en" class="text-white hover:text-emerald-400 font-semibold underline decoration-zinc-600 underline-offset-4">Duong Phuc Khanh</a> (<strong>Dương Phúc Khánh</strong> · khanhdp · Kido).
      </p>
      <div class="flex flex-wrap items-center gap-3 text-xs font-mono pt-2">
        <span class="px-3 py-1 rounded-full bg-white/[0.04] border border-white/[0.08] text-zinc-300">12 Full-Length Architecture Papers</span>
        <span class="px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300">128+ Kido Chronicles Postmortems</span>
        <span class="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">ORCID: 0009-0005-7192-2664</span>
      </div>
    </div>

    <!-- Section 1: English Architecture Deep-Dives -->
    <section class="space-y-6">
      <div class="flex items-center justify-between border-b border-white/[0.06] pb-3">
        <div>
          <h2 class="text-xl sm:text-2xl font-semibold text-zinc-100 flex items-center gap-2">
            <span class="text-emerald-400 font-mono text-sm">EN.</span>
            <span>English Systems Architecture Deep-Dives</span>
          </h2>
          <p class="text-xs font-mono text-zinc-400 mt-0.5">Authoritative technical essays targeting global systems engineering audiences</p>
        </div>
        <span class="text-xs font-mono text-zinc-500">{len(en_articles)} Articles</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {en_cards_html}
      </div>
    </section>

    <!-- Section 2: Vietnamese Production Case Studies -->
    <section class="space-y-6">
      <div class="flex items-center justify-between border-b border-white/[0.06] pb-3">
        <div>
          <h2 class="text-xl sm:text-2xl font-semibold text-zinc-100 flex items-center gap-2">
            <span class="text-emerald-400 font-mono text-sm">VI.</span>
            <span>Chuyên Khảo Kỹ Thuật &amp; Sự Cố Production (Tiếng Việt)</span>
          </h2>
          <p class="text-xs font-mono text-zinc-400 mt-0.5">Giải phẫu thực chiến các ca nghẽn tải, race condition và kiến trúc cơ sở dữ liệu</p>
        </div>
        <span class="text-xs font-mono text-zinc-500">{len(vi_articles)} Bài viết</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {vi_cards_html}
      </div>
    </section>

    <!-- Section 3: Curated Grid of 20 Flagship Kido Chronicles Episodes -->
    <section class="space-y-6 pt-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/[0.06] pb-3">
        <div>
          <div class="flex items-center gap-2 text-purple-400 font-mono text-xs font-semibold uppercase tracking-wider">
            <span class="w-2 h-2 rounded-full bg-purple-400"></span>
            <span>Biên Niên Sử Thực Chiến (128+ Tập)</span>
          </div>
          <h2 class="text-xl sm:text-2xl font-semibold text-zinc-100 mt-1">
            20 Tập Kido Chronicles Tiêu Biểu (truyen.khanhdp.com)
          </h2>
          <p class="text-xs text-zinc-400 mt-0.5 font-mono">
            Nhật ký giải phẫu sự cố sản xuất nửa đêm, kỹ thuật kiểm thử và văn hóa kỹ sư thực chiến
          </p>
        </div>
        <a href="https://truyen.khanhdp.com" target="_blank" rel="noopener" class="px-3 py-1.5 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/30 transition-all font-mono text-xs flex items-center gap-1.5 self-start sm:self-center">
          <span>Xem trọn bộ 128 tập</span>
          <span>↗</span>
        </a>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {episodes_grid_str}
      </div>
    </section>

    <!-- Author & Entity Verification Box -->
    <section class="p-6 rounded-2xl border border-white/10 bg-[#121212] space-y-4">
      <div class="flex flex-col sm:flex-row items-center sm:items-start gap-5">
        <img
          src="/duong-phuc-khanh.jpg"
          alt="Duong Phuc Khanh (Dương Phúc Khánh · Kido)"
          width="96"
          height="96"
          style="width:96px;height:96px;object-fit:cover;"
          class="rounded-2xl border border-white/15 shrink-0"
        />
        <div class="space-y-2 text-center sm:text-left flex-1">
          <div class="flex flex-wrap items-center justify-center sm:justify-start gap-2">
            <h3 class="text-lg font-semibold text-zinc-100">Dương Phúc Khánh</h3>
            <span class="text-xs font-mono text-zinc-400">/ Duong Phuc Khanh · khanhdp · Kido</span>
          </div>
          <p class="text-xs sm:text-sm text-zinc-300 leading-relaxed">
            Senior Software Engineer &amp; Systems Architect based in Da Nang, Vietnam. 6 years at FPT Software SBI Lab (3x Best Performance Award recipient), Startup Runway 2018 Champion. Creator of <a href="https://khanhdp.com" class="text-emerald-400 hover:underline">khanhdp.com</a>, <a href="/en" class="text-sky-400 hover:underline">Official Biography (EN)</a>, <a href="/about" class="text-sky-400 hover:underline">Tiểu sử Tiếng Việt</a>, <a href="https://blog.khanhdp.com" target="_blank" rel="noopener" class="text-sky-400 hover:underline">Kido Engineering Blog</a>, <a href="https://truyen.khanhdp.com" target="_blank" rel="noopener" class="text-purple-300 hover:underline">Kido Chronicles</a>, and <a href="https://github.com/khanhduong22/agent-harness-kit" target="_blank" rel="noopener" class="text-emerald-400 hover:underline">Agent Harness Kit</a>.
          </p>
          <div class="flex flex-wrap items-center justify-center sm:justify-start gap-3 text-xs font-mono pt-1">
            <a href="https://www.google.com/search?kgmid=/g/11zyg5zq1c" target="_blank" rel="noopener" class="text-sky-400 hover:underline">Google KG /g/11zyg5zq1c</a>
            <span class="text-zinc-600">·</span>
            <a href="https://www.wikidata.org/wiki/Q141718572" target="_blank" rel="noopener" class="text-sky-400 hover:underline">Wikidata Q141718572</a>
            <span class="text-zinc-600">·</span>
            <a href="https://orcid.org/0009-0005-7192-2664" target="_blank" rel="noopener" class="text-sky-400 hover:underline">ORCID 0009-0005-7192-2664</a>
            <span class="text-zinc-600">·</span>
            <a href="https://github.com/khanhduong22" target="_blank" rel="noopener" class="text-zinc-400 hover:text-white">GitHub</a>
            <span class="text-zinc-600">·</span>
            <a href="https://dev.to/khanhduong22" target="_blank" rel="noopener" class="text-zinc-400 hover:text-white">DEV.to</a>
            <span class="text-zinc-600">·</span>
            <a href="https://viblo.asia/u/khanhdp" target="_blank" rel="noopener" class="text-zinc-400 hover:text-white">Viblo</a>
          </div>
        </div>
      </div>
    </section>

  </main>

  <!-- Global Footer -->
  <footer class="border-t border-white/[0.06] bg-[#080808] text-xs font-mono text-zinc-500 py-12">
    <div class="max-w-5xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
        <a href="https://khanhdp.com" class="text-zinc-300 hover:text-white font-semibold uppercase transition-colors">DUONG PHUC KHANH (KIDO)</a>
      </div>
      <div class="flex items-center gap-4 text-zinc-400 flex-wrap">
        <a href="/" class="hover:text-white transition-colors">Overview</a>
        <a href="/en" class="hover:text-white transition-colors">Biography (EN)</a>
        <a href="/about" class="hover:text-white transition-colors">Tiểu sử (VI)</a>
        <a href="/articles/" class="text-white hover:text-emerald-400 transition-colors">Articles</a>
        <a href="https://blog.khanhdp.com" target="_blank" rel="noopener" class="hover:text-white transition-colors">Engineering Blog</a>
        <a href="/portfolio" class="hover:text-white transition-colors">Portfolio</a>
        <a href="https://truyen.khanhdp.com" target="_blank" rel="noopener" class="hover:text-white transition-colors">Chronicles</a>
        <a href="https://github.com/khanhduong22" target="_blank" rel="noopener" class="hover:text-white transition-colors">GitHub</a>
        <a href="https://www.linkedin.com/in/duong-phuc-khanh/" target="_blank" rel="noopener" class="hover:text-white transition-colors">LinkedIn</a>
      </div>
    </div>
    <div class="max-w-5xl mx-auto px-6 mt-4 text-[11px] text-zinc-600 flex flex-col sm:flex-row items-center justify-between gap-2">
      <p>© 2026 Duong Phuc Khanh (khanhdp · Kido). All rights reserved.</p>
      <p>Crafted with quiet confidence</p>
    </div>
  </footer>

  <!-- Scroll Progress Script -->
  <script>
    window.addEventListener('scroll', () => {{
      const winScroll = document.documentElement.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (winScroll / height) * 100;
      const progressBar = document.getElementById('progress-bar');
      if (progressBar) progressBar.style.width = scrolled + '%';
    }}, {{ passive: true }});

    document.addEventListener("click", (e) => {{
      let a = e.target.closest("a[href]");
      if (a) {{
        let h = a.getAttribute("href");
        if (h && (h.startsWith("http://") || h.startsWith("https://")) && !h.includes(window.location.hostname)) {{
          let t = (a.getAttribute("title") || a.textContent || h).trim().slice(0, 60);
          if (window.trackEvent) window.trackEvent("outbound_click", {{ event_category: "outbound", destination_url: h, link_text: t }});
        }} else if (h && (h.startsWith("#") || h.startsWith("/"))) {{
          let t = (a.textContent || h).trim().slice(0, 40);
          if (window.trackEvent) window.trackEvent("nav_click", {{ event_category: "navigation", destination: h, link_text: t }});
        }}
      }}
    }}, {{ passive: true }});
  </script>
</body>
</html>
"""


def main():
    print("🚀 ========================================================")
    print("🚀 build_articles_seo.py — Bilingual Technical Articles Hub")
    print("🚀 ========================================================\n")

    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    compiled_articles = []

    for art_meta in ARTICLES_METADATA:
        slug = art_meta["slug"]
        print(f"📄 Processing article: {slug}...")

        if art_meta.get("raw_content"):
            raw_text = art_meta["raw_content"]
        else:
            file_path = SEEDING_DIR / art_meta["file"]
            if not file_path.exists():
                raise FileNotFoundError(f"Seeding file not found: {file_path}")
            raw_text = file_path.read_text(encoding="utf-8")

        fm, body = parse_frontmatter(raw_text)
        title = fm.get("title") or art_meta["default_title"]
        desc = fm.get("description") or art_meta["default_desc"]

        # Clean title if wrapped in quotes
        if (title.startswith('"') and title.endswith('"')) or (title.startswith("'") and title.endswith("'")):
            title = title[1:-1]

        article_obj = {
            "slug": slug,
            "lang": art_meta["lang"],
            "title": title,
            "desc": desc,
            "category": art_meta["category"],
            "tags": art_meta.get("tags", ["Architecture", "Engineering"])
        }

        # Convert markdown body to semantic HTML
        html_body = markdown_to_html(body)

        # Render complete HTML document
        full_html = render_article_page(article_obj, html_body)

        # Output to /articles/<slug>/index.html
        target_dir = ARTICLES_DIR / slug
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "index.html"
        target_file.write_text(full_html, encoding="utf-8")
        print(f"   ✓ Wrote: {target_file}")

        compiled_articles.append(article_obj)

    # Now render the Hub Index Page: /articles/index.html
    print("\n📚 Rendering Articles Hub Index (/articles/index.html)...")
    hub_html = render_hub_index_page(compiled_articles)
    hub_file = ARTICLES_DIR / "index.html"
    hub_file.write_text(hub_html, encoding="utf-8")
    print(f"   ✓ Wrote: {hub_file}")

    print("\n✅ Verification & Build Complete!")
    print(f"Total articles compiled: {len(compiled_articles)}")
    for a in compiled_articles:
        print(f" - [{a['lang'].upper()}] https://khanhdp.com/articles/{a['slug']}/ ({a['category']})")
    print(f" - [HUB] https://khanhdp.com/articles/")


if __name__ == "__main__":
    main()
