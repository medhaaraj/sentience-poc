# Sentience – AI Usage Governance Platform

## Overview

Sentience is an AI Usage Governance Platform designed to help organizations gain visibility into how employees use AI tools across their environment. It identifies AI services accessed through network telemetry and classifies them as licensed or shadow AI, helping organizations monitor adoption and improve governance.

The platform brings together telemetry monitoring, AI tool detection, usage analytics, and an AI-powered assistant to provide a centralized view of enterprise AI usage.

## Key Features

- **AI Tool Detection:** Identifies AI services accessed across the organization's network using telemetry data.
- **Licensed vs. Shadow AI Classification:** Distinguishes approved AI tools from unapproved or unregistered services.
- **Usage Analytics:** Aggregates AI usage data to highlight tool adoption, user activity, and usage trends.
- **Centralized Dashboard:** Provides a visual overview of AI tools, usage patterns, and governance insights.
- **AI-Powered Assistant:** Uses the OpenAI API to answer natural-language questions about governance data and generate usage summaries.
- **Structured APIs:** Provides organized access to AI tool information and usage data through MCP-style APIs.

## System Architecture

Sentience follows a modular architecture that connects telemetry collection, backend processing, data storage, analytics, and visualization.

**High-level workflow:**

1. Network telemetry provides information about accessed domains and services.
2. The backend processes incoming events and identifies associated AI tools.
3. Detected tools are classified based on their licensing status.
4. Usage information is stored and aggregated in PostgreSQL.
5. APIs expose structured governance data to the dashboard and AI assistant.
6. The dashboard presents usage insights, while the AI assistant enables natural-language interaction with the data.

## Technology Stack

| Component | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Telemetry Simulation | Cloudflare Workers |
| Containerization | Docker, Docker Compose |
| APIs | REST APIs, MCP-style APIs |
| AI Integration | OpenAI API |
| Frontend | Web-based dashboard |

## Project Objective

The objective of Sentience is to make enterprise AI usage more transparent by helping organizations identify the AI tools being accessed, understand adoption patterns, distinguish approved usage from shadow AI, and make informed governance decisions.

## Future Scope

- Integration with live enterprise Secure Web Gateway telemetry.
- Advanced AI usage anomaly detection.
- Role-based access control and governance policies.
- Enhanced analytics and reporting.
- Expanded AI-powered recommendations and insights.
