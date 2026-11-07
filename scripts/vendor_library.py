#!/usr/bin/env python3
"""Vendor the curated ECC packs into library/<category>/<name>/.

Reproducible: the manifest below is the curation decision. Re-run against a fresh
ECC checkout with --from <path>/ecc/skills.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

CURATION = {
    "lang": [
        "python-patterns", "python-testing", "typescript-patterns",
        "golang-patterns", "golang-testing", "rust-patterns", "rust-testing",
        "java-coding-standards", "kotlin-patterns", "kotlin-testing",
        "swiftui-patterns", "swift-concurrency-6-2", "dotnet-patterns",
        "cpp-coding-standards", "cpp-testing", "perl-patterns", "dart-flutter-patterns",
    ],
    "web": [
        "react-patterns", "react-performance", "react-testing", "vue-patterns",
        "angular-developer", "nextjs-turbopack", "nuxt4-patterns", "vite-patterns",
        "frontend-patterns", "frontend-a11y", "accessibility", "motion-patterns",
        "design-system", "make-interfaces-feel-better", "inherit-legacy-style",
    ],
    "backend": [
        "api-design", "backend-patterns", "error-handling", "postgres-patterns",
        "mysql-patterns", "redis-patterns", "clickhouse-io", "database-migrations",
        "prisma-patterns", "nestjs-patterns", "laravel-patterns", "rails-patterns",
        "django-patterns", "django-security", "fastapi-patterns", "springboot-patterns",
        "springboot-security", "jpa-patterns", "contract-first", "mcp-server-patterns",
    ],
    "infra": [
        "docker-patterns", "kubernetes-patterns", "deployment-patterns",
        "prompt-caching-strategy", "cost-aware-llm-pipeline",
    ],
    "data": ["pytorch-patterns", "mle-workflow", "eval-harness", "ai-regression-testing"],
    "security": [
        "security-review", "agent-security-hardening", "mcp-dependency-review",
        "security-bounty-hunter", "osint-investigation",
    ],
    "quality": [
        "e2e-testing", "test-collaboration", "windows-desktop-e2e", "benchmark",
        "benchmark-optimization-loop",
    ],
    "product": [
        "architecture-decision-records", "product-lens", "intent-driven-development",
        "codebase-onboarding", "code-tour", "search-first", "council", "santa-method",
        "ai-first-engineering", "production-audit",
    ],
    "agent": [
        "agentic-engineering", "agent-architecture-audit", "agent-introspection-debugging",
        "agent-self-evaluation", "parallel-execution-optimizer", "loop-design-check",
        "gan-style-harness", "skill-stocktake", "rules-distill", "unified-memory",
        "safety-guard",
    ],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", default="../ecc/skills", help="path to ecc/skills")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()

    src = Path(args.src).resolve()
    if not src.is_dir():
        print(f"source not found: {src}", file=sys.stderr)
        return 2
    dst = Path(args.root).resolve() / "library"
    missing, copied = [], 0
    for category, names in CURATION.items():
        for name in names:
            s = src / name
            if not (s / "SKILL.md").is_file():
                missing.append(f"{category}/{name}")
                continue
            d = dst / category / name
            if d.exists():
                shutil.rmtree(d)
            shutil.copytree(s, d, ignore=shutil.ignore_patterns("__pycache__", ".git"))
            copied += 1
    print(f"copied {copied} packs into {dst}")
    if missing:
        print("missing upstream: " + ", ".join(missing), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
