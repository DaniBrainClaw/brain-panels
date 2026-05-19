# AI Marketing Suite for Claude Code - ai-marketing-claude

Source: https://github.com/zubair-trabzada/ai-marketing-claude

A comprehensive marketing analysis and automation skill system for Claude Code. Audit any website's marketing, generate copy, build email sequences, create content calendars, analyze competitors, and produce client-ready PDF reports.

Built for entrepreneurs, agency builders, and solopreneurs who want to sell marketing services powered by AI.

## Commands

- /market audit <url> - Full marketing audit with 5 parallel agents
- /market quick <url> - 60-second marketing snapshot
- /market copy <url> - Generate optimized copy
- /market emails <topic> - Generate complete email sequences
- /market social <topic> - 30-day social media content calendar
- /market ads <url> - Ad creative and copy for all platforms
- /market funnel <url> - Sales funnel analysis
- /market competitors <url> - Competitive intelligence report
- /market landing <url> - Landing page CRO analysis
- /market launch <product> - Product launch playbook
- /market proposal <client> - Client proposal generator
- /market report <url> - Full marketing report (Markdown)
- /market report-pdf <url> - Professional marketing report (PDF)
- /market seo <url> - SEO content audit
- /market brand <url> - Brand voice analysis

## Project Structure

- market/SKILL.md - Main orchestrator
- skills/ - 14 sub-skills for different marketing functions
- agents/ - 5 parallel subagents for analysis
- scripts/ - Python utility scripts
- templates/ - Marketing templates

## Marketing Audit Scoring

Weights: Content & Messaging (25%), Conversion Optimization (20%), SEO & Discoverability (20%), Competitive Positioning (15%), Brand & Trust (10%), Growth & Strategy (10%)