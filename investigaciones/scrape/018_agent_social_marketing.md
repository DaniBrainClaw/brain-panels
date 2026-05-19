# Agent Social Marketing - Multi-Agent Content Marketing System

Source: https://github.com/agentuity/agent-social-marketing

The Content Marketing Agent System is an AI-powered automation platform for creating, managing, and scheduling social media content. Built with Agentuity and TypeScript, this system automates the entire content marketing workflow from topic ideation to post scheduling.

## Architecture

Multi-agent system with three specialized agents:
- Manager Agent: Orchestrates the entire content marketing workflow
- Copywriter Agent: Creates engaging social media content for different platforms
- Scheduler Agent: Schedules content for publishing through Typefully API

## Manager Agent

- Inputs: Topic, optional description, publish date, and domain source
- Functions: Extracts structured information, checks for existing campaigns, creates new campaigns, hands off to Copywriter Agent
- Outputs: Campaign data or handoff to Copywriter Agent

## Copywriter Agent

- Inputs: Campaign ID, topic, and optional description
- Functions: Generates LinkedIn posts with hashtags, creates Twitter threads, saves content to campaign
- Outputs: LinkedIn posts and Twitter threads

## Scheduler Agent

- Inputs: Campaign ID and optional publish date
- Functions: Interfaces with Typefully API, schedules posts, updates campaign status
- Outputs: Scheduling confirmation with links

## Requirements

- Bun v1.2.5 or higher
- Agentuity CLI (for development)
- Typefully API key (for scheduling content)