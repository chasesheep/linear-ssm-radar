#!/usr/bin/env python3
"""Linear Attention / SSM / Hybrid Research Radar - Daily Scan"""
import os, sys, json, re, urllib.request, urllib.parse, time, datetime
from datetime import datetime, timezone, timedelta

TOKEN = os.environ.get("RESEARCH_RADAR_GITHUB_TOKEN", "")
TODAY = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
REPO_DIR = "/root/linear-ssm-radar"

def gh_api(path):
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "research-radar/1.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

def arxiv_api(query, start=0, max_results=100):
    """Search arXiv with given query."""
    q = urllib.parse.quote(query)
    url = f"http://export.arxiv.org/api/query?search_query={q}&start={start}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            return resp.read().decode()
    except Exception as e:
        return ""

def parse_arxiv_feed(xml_text):
    """Parse arXiv Atom feed to list of entries."""
    entries = []
    entry_pattern = re.compile(r'<entry>(.*?)</entry>', re.DOTALL)
    title_pattern = re.compile(r'<title>(.*?)</title>', re.DOTALL)
    summary_pattern = re.compile(r'<summary>(.*?)</summary>', re.DOTALL)
    id_pattern = re.compile(r'<id>http://arxiv.org/abs/([^<]+)</id>')
    published_pattern = re.compile(r'<published>([^<]+)</published>')
    author_pattern = re.compile(r'<name>([^<]+)</name>')
    
    for m in entry_pattern.finditer(xml_text):
        entry_text = m.group(1)
        title = title_pattern.search(entry_text)
        summary = summary_pattern.search(entry_text)
        arxiv_id = id_pattern.search(entry_text)
        published = published_pattern.search(entry_text)
        authors = author_pattern.findall(entry_text)
        
        if arxiv_id:
            entries.append({
                "id": arxiv_id.group(1).strip(),
                "title": (title.group(1) if title else "").replace('\n', ' ').strip(),
                "summary": (summary.group(1) if summary else "").replace('\n', ' ').strip(),
                "published": published.group(1) if published else "",
                "authors": authors,
                "url": f"https://arxiv.org/abs/{arxiv_id.group(1).strip()}",
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id.group(1).strip()}.pdf"
            })
    return entries

def score_paper(entry):
    """Score paper relevance per Design Brief rubric."""
    title = entry["title"].lower()
    summary = entry["summary"].lower()
    text = title + " " + summary
    
    # Scope match
    scope_keywords = [
        "linear attention", "state space model", "structured state space", "selective state space",
        "mamba", "mamba-2", "recurrent language model", "recurrent llm", "hybrid attention",
        "hybrid ssm", "attention-ssm", "linear rnn", "xlstm", "rwkv", "retnet", "deltanet",
        "gated linear attention", "glatt", "kv cache", "cache compression", "long-context inference",
        "efficient long context", "recurrent inference", "streaming inference", "selective scan",
        "parallel scan", "chunkwise", "fused kernel", "triton kernel", "flash linear attention"
    ]
    scope_match = 0
    for kw in scope_keywords:
        if kw in text:
            scope_match = min(3, scope_match + 1)
    if scope_match > 0:
        scope_match = min(3, scope_match + 1)  # boost if any match
    
    # Negative terms
    negative = ["graph transformer", "molecular", "protein", "ai4science", "hyperspectral",
                "medical image segmentation", "object detection", "remote sensing", "point cloud",
                "diffusion model", "image restoration", "low precision", "quantization", "fp4"]
    neg_count = sum(1 for n in negative if n in text)
    if neg_count >= 2:
        scope_match = max(0, scope_match - 1)
    
    # Technical signal
    tech_signal = 0
    if any(x in text for x in ["kernel", "implementation", "code", "benchmark", "fused"]):
        tech_signal = min(3, tech_signal + 1)
    if any(x in text for x in ["architecture", "mechanism", "theoretical", "analysis"]):
        tech_signal = min(3, tech_signal + 1)
    if len(entry["summary"]) > 500:
        tech_signal = min(3, tech_signal + 1)
    
    # Source strength (arXiv is normal)
    source_strength = 1
    
    # Actionability
    actionability = min(3, scope_match)
    
    # Relation to work (simplified)
    relation = 0
    if any(x in text for x in ["hybrid", "anchor", "attention-ssm", "gated linear"]):
        relation = min(3, relation + 2)
    if any(x in text for x in ["mamba", "linear attention", "recurrent"]):
        relation = min(3, relation + 1)
    
    total = scope_match + tech_signal + relation + source_strength + actionability
    
    return {
        "scope_match": scope_match,
        "technical_signal": tech_signal,
        "relation_to_our_work": relation,
        "source_strength": source_strength,
        "actionability": actionability,
        "total": total
    }

def classify_action(scores):
    total = scores["total"]
    sm = scores["scope_match"]
    if sm >= 2 and total >= 9:
        return "deep_read"
    elif sm >= 2 and total >= 6:
        return "read"
    elif sm >= 2:
        return "watch"
    return "ignore"

def main():
    print(f"=== Research Radar Scan: {TODAY} ===\n")
    
    # 0. Key author scan (aviv bick et al.)
    print("0. Scanning key authors on arXiv...")
    key_authors = [
        ("au:%22Albert+Gu%22", "Albert Gu"),
        ("au:%22Tri+Dao%22", "Tri Dao"),
        ("au:%22Aviv+Bick%22", "Aviv Bick"),
        ("au:%22Songlin+Yang%22", "Songlin Yang"),
        ("au:%22Yoon+Kim%22", "Yoon Kim"),
        ("au:%22Christopher+Ré%22", "Christopher Ré"),
        ("au:%22J.+Zico+Kolter%22", "J. Zico Kolter"),
        ("au:%22Kevin+Y.+Li%22", "Kevin Y. Li"),
        ("au:%22Aakash+Lahoti%22", "Aakash Lahoti"),
        ("au:%22Berlin+Chen%22", "Berlin Chen"),
    ]
    author_entries = []
    for au_code, au_name in key_authors:
        print(f"   Checking {au_name} ({au_code})...")
        xml = arxiv_api(au_code, max_results=10)
        entries = parse_arxiv_feed(xml)
        for e in entries:
            e["scores"] = score_paper(e)
            e["action"] = classify_action(e["scores"])
            e["_author_search"] = au_name
            author_entries.append(e)
        time.sleep(3)
    print(f"   Found {len(author_entries)} papers from key authors\n")
    
    # 1. arXiv Scan
    print("1. Scanning arXiv...")
    arxiv_query = 'cat:cs.CL OR cat:cs.LG OR cat:cs.AI OR cat:stat.ML'
    # Search with key terms
    all_entries = []
    
    # Multiple search queries for coverage
    queries = [
        'all:"linear attention"',
        'all:"state space model" OR all:"selective state space"',
        'all:"mamba" AND (all:"language" OR all:"sequence" OR all:"model")',
        'all:"recurrent language model" OR all:"recurrent LLM"',
        'all:"hybrid attention" OR all:"attention-SSM"',
        'all:"KV cache" AND (all:"efficient" OR all:"compression" OR all:"recurrent")',
        'all:"flash linear attention" OR all:"gated linear attention"',
        'all:"chunkwise" OR all:"selective scan"',
    ]
    
    seen_ids = set()
    for q in queries:
        print(f"   Query: {q}")
        xml = arxiv_api(q, max_results=30)
        entries = parse_arxiv_feed(xml)
        for e in entries:
            if e["id"] not in seen_ids:
                seen_ids.add(e["id"])
                e["scores"] = score_paper(e)
                e["action"] = classify_action(e["scores"])
                all_entries.append(e)
        time.sleep(3)  # Be polite to arXiv
    
    print(f"   Found {len(all_entries)} unique papers")
    
    # Filter to recent 48h
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
    recent = []
    for e in all_entries + author_entries:
        try:
            pub = datetime.fromisoformat(e["published"].replace('Z', '+00:00'))
            if pub >= cutoff:
                recent.append(e)
        except:
            pass
    
    # Deduplicate by arxiv ID
    seen_ids = set()
    deduped = []
    for e in recent:
        if e["id"] not in seen_ids:
            seen_ids.add(e["id"])
            deduped.append(e)
    recent = deduped
    
    # Sort by total score
    recent.sort(key=lambda x: x["scores"]["total"], reverse=True)
    
    must_check = [e for e in recent if e["action"] == "deep_read"]
    watch = [e for e in recent if e["action"] == "read"]
    
    print(f"   Recent 48h: {len(recent)} papers")
    print(f"   Must-check: {len(must_check)}")
    print(f"   Watch: {len(watch)}\n")
    
    # 2. GitHub Scan
    print("2. Scanning GitHub core repos...")
    repos = [
        ("fla-org/flash-linear-attention", "very_high"),
        ("state-spaces/mamba", "very_high"),
    ]
    
    gh_events = []
    for repo, priority in repos:
        print(f"   Checking {repo}...")
        # Recent releases
        releases = gh_api(f"/repos/{repo}/releases?per_page=5")
        if isinstance(releases, list):
            for r in releases:
                published = r.get("published_at", "")
                try:
                    pub_dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    if pub_dt >= cutoff:
                        gh_events.append({
                            "type": "release",
                            "repo": repo,
                            "title": r.get("name", ""),
                            "body": r.get("body", "")[:500],
                            "url": r.get("html_url", ""),
                            "published": published,
                            "tag": r.get("tag_name", "")
                        })
                except:
                    pass
        
        # Recent PRs
        prs = gh_api(f"/repos/{repo}/pulls?state=closed&sort=updated&direction=desc&per_page=10")
        if isinstance(prs, list):
            for pr in prs:
                merged = pr.get("merged_at")
                if merged:
                    try:
                        mdt = datetime.fromisoformat(merged.replace('Z', '+00:00'))
                        if mdt >= cutoff:
                            gh_events.append({
                                "type": "pr_merged",
                                "repo": repo,
                                "title": pr.get("title", ""),
                                "url": pr.get("html_url", ""),
                                "merged_at": merged,
                                "author": pr.get("user", {}).get("login", "")
                            })
                    except:
                        pass
        
        # Recent issues (important ones)
        issues = gh_api(f"/repos/{repo}/issues?state=all&sort=updated&direction=desc&per_page=10")
        if isinstance(issues, list):
            for issue in issues:
                if "pull_request" in issue:
                    continue
                updated = issue.get("updated_at", "")
                try:
                    udt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                    if udt >= cutoff:
                        labels = [l.get("name", "") for l in issue.get("labels", [])]
                        gh_events.append({
                            "type": "issue",
                            "repo": repo,
                            "title": issue.get("title", ""),
                            "url": issue.get("html_url", ""),
                            "updated_at": updated,
                            "labels": labels,
                            "state": issue.get("state", "")
                        })
                except:
                    pass
        
        time.sleep(1)
    
    print(f"   Found {len(gh_events)} recent events\n")
    
    # 3. Write outputs
    print("3. Writing outputs...")
    
    # Raw events JSONL
    raw_events = []
    event_id = 0
    
    for e in must_check + watch:
        event_id += 1
        raw_events.append({
            "event_id": f"arxiv-{TODAY}-{event_id:03d}",
            "date": TODAY,
            "source": "arXiv",
            "event_type": "paper",
            "title": e["title"],
            "url": e["url"],
            "authors": e["authors"],
            "labs": [],
            "repos": [],
            "models": [],
            "concepts": [],
            "artifact": {"paper_url": e["url"], "code_url": None, "model_url": None, "blog_url": None, "slides_url": None},
            "abstract_or_snippet": e["summary"][:500],
            "matched_scope": ["linear attention" if "linear attention" in e["title"].lower() else ""],
            "scores": e["scores"],
            "relevance": "high" if e["action"] == "deep_read" else "medium",
            "confidence": "medium",
            "why_relevant": f"Score: {e['scores']['total']}" + (f" [author: {e.get('_author_search', '')}]" if '_author_search' in e else ""),
            "relation_to_our_work": "useful_related_work",
            "recommended_action": e["action"],
            "evidence_quote_or_snippet": e["summary"][:300]
        })
    
    for e in gh_events:
        event_id += 1
        etype = "code_release" if e["type"] == "release" else "repo_update"
        raw_events.append({
            "event_id": f"github-{TODAY}-{event_id:03d}",
            "date": TODAY,
            "source": "GitHub",
            "event_type": etype,
            "title": e["title"],
            "url": e["url"],
            "authors": [e.get("author", "")],
            "labs": [],
            "repos": [e["repo"]],
            "models": [],
            "concepts": [],
            "artifact": {"paper_url": None, "code_url": e["url"], "model_url": None, "blog_url": None, "slides_url": None},
            "abstract_or_snippet": e.get("body", "")[:500] if "body" in e else "",
            "matched_scope": [e["repo"].split("/")[-1]],
            "scores": {"scope_match": 3, "technical_signal": 2, "relation_to_our_work": 2, "source_strength": 2, "actionability": 2, "total": 11},
            "relevance": "high",
            "confidence": "high",
            "why_relevant": f"{e['type']} from {e['repo']}",
            "relation_to_our_work": "implementation_signal",
            "recommended_action": "inspect_code",
            "evidence_quote_or_snippet": e.get("body", "")[:200] if "body" in e else e["title"]
        })
    
    # Write JSONL
    jsonl_path = f"{REPO_DIR}/data/raw_events/{TODAY}.jsonl"
    with open(jsonl_path, "w") as f:
        for ev in raw_events:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    print(f"   Written: {jsonl_path}")
    
    # Write daily report
    report_path = f"{REPO_DIR}/reports/daily/{TODAY}.md"
    with open(report_path, "w") as f:
        f.write(f"# Linear Attention / SSM / Hybrid Research Radar — {TODAY}\n\n")
        f.write(f"*Scan time: {datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')} CST*\n\n")
        
        f.write("## 1. Must-check research events\n\n")
        if must_check:
            for i, e in enumerate(must_check, 1):
                f.write(f"### Event {i}: {e['title']}\n")
                f.write(f"- **Type:** paper\n")
                f.write(f"- **Source:** arXiv\n")
                f.write(f"- **URL:** {e['url']}\n")
                f.write(f"- **One-line take:** {e['summary'][:200]}...\n")
                f.write(f"- **Scores:** scope={e['scores']['scope_match']}, tech={e['scores']['technical_signal']}, relation={e['scores']['relation_to_our_work']}, total={e['scores']['total']}\n")
                f.write(f"- **Recommended action:** {e['action']}\n\n")
        else:
            f.write("No must-check papers found in the last 48 hours.\n\n")
        
        f.write("## 2. Artifact releases\n\n")
        gh_releases = [e for e in gh_events if e["type"] == "release"]
        if gh_releases:
            for e in gh_releases:
                f.write(f"- **{e['repo']}** — [{e['title']}]({e['url']}) (`{e['tag']}`)\n")
        else:
            f.write("No new releases from core repos in the last 48 hours.\n")
        
        f.write("\n## 3. GitHub activity\n\n")
        gh_prs = [e for e in gh_events if e["type"] == "pr_merged"]
        gh_issues = [e for e in gh_events if e["type"] == "issue"]
        if gh_prs:
            f.write("### Merged PRs\n")
            for e in gh_prs:
                f.write(f"- [{e['repo']}] [{e['title']}]({e['url']}) by @{e['author']}\n")
            f.write("\n")
        if gh_issues:
            f.write("### Recent Issues\n")
            for e in gh_issues:
                f.write(f"- [{e['repo']}] [{e['title']}]({e['url']}) [{e['state']}]\n")
            f.write("\n")
        if not gh_prs and not gh_issues:
            f.write("No significant PR or issue activity in the last 48 hours.\n\n")
        
        f.write("## 4. Watch\n\n")
        if watch:
            for e in watch:
                f.write(f"- [{e['title']}]({e['url']}) — score: {e['scores']['total']}\n")
        else:
            f.write("No watch-tier papers found.\n\n")
        
        f.write("## 5. Source expansion proposals\n\n")
        f.write("_No new sources identified today._\n\n")
        
        f.write("## 6. Uncertainty and possible misses\n\n")
        f.write("- Hugging Face papers/models not scanned yet\n")
        f.write("- Manual sources (Discord, blogs) require manual input\n")
        f.write("- arXiv search coverage depends on keyword matching\n")
    
    print(f"   Written: {report_path}")
    print(f"\n=== Scan complete: {len(raw_events)} total events ===")

if __name__ == "__main__":
    main()
