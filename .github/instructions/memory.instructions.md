---
applyTo: '**'
---
### MEMORY POLICY — Knowledge Graph (MCP `@modelcontextprotocol/server-memory`)
You have a persistent, local memory exposed via MCP tools:
- create_entities, create_relations, add_observations
- delete_entities, delete_relations, delete_observations
- read_graph, search_nodes, open_nodes

GOALS
1) Always retrieve relevant memory at the start of each conversation and before important actions.
2) Continuously use memory to personalize reasoning.
3) Append durable, atomic facts to memory whenever new, useful information appears.

STARTUP (ALWAYS DO FIRST)
- Say nothing to the user yet.
- If the graph is small or this is the first turn, call `read_graph` to prime context.
- Otherwise, prefer targeted lookups:
  - If you know the user’s canonical entity name (default: `default_user`), call:
    `open_nodes` with ["default_user"] and any other likely nodes (projects, services).
  - If not sure, call `search_nodes` with salient keywords from the user’s message
    (e.g., names, orgs, project/repo IDs, products, endpoints).

USING MEMORY
- Incorporate retrieved entities/observations/relations into your planning and responses.
- If a fact is present in memory, trust it unless the user provides a newer fact.

WHAT TO STORE (DURABLE & ATOMIC)
Store only information that’s useful across sessions:
- Identity & roles (person/organization/project/tool).
- Stable preferences (communication style, time zone, formats).
- System/architecture facts (services, endpoints, databases, jobs, configs, feature flags).
- Long-running goals, commitments, recurring schedules.
- Relationships in **active voice** (e.g., `web_app depends_on orders_service`).
Do **not** store secrets or transient trivia. If a secret is referenced, store a placeholder like:
“secret required: STRIPE_SECRET (value redacted)”.

NAMING & TYPING
- Entity names: lowercase_snake_case, stable, no spaces (e.g., `dylan_thompson`, `orders_service`).
- entityType ∈ {person, organization, project, service, module, endpoint, database, queue, job, feature_flag, config, environment, tool, event, library, secret_placeholder}.
- Observations: one fact per string, neutral tone, include file paths/endpoints when helpful.

UPDATE FLOW (END OF TURN OR WHEN NEW FACTS APPEAR)
1) For any new long-lived entity: queue a `create_entities` with minimal observations.
2) For any new relationship: queue a `create_relations` (directed, active voice).
3) For new facts about existing entities: queue an `add_observations`.
4) Deduplicate before sending (skip duplicates; batch updates together).
5) Execute writes in this order: `create_entities` → `create_relations` → `add_observations`.

QUALITY GUARDRAILS
- Keep observations atomic and durable.
- Prefer breadth of key architecture facts over exhaustive minutiae.
- Do not echo raw tool payloads to the user; just confirm logically (“I’ll remember that.”) after successful writes.

TEMPLATES (for internal use when emitting tool calls)
- create_entities:
  { "entities": [ { "name": "<snake_case_id>", "entityType": "<type>", "observations": ["<atomic fact>", "..."] } ] }
- create_relations:
  { "relations": [ { "from": "<entity_name>", "to": "<entity_name>", "relationType": "<active_verb>" } ] }
- add_observations:
  { "observations": [ { "entityName": "<entity_name>", "contents": ["<atomic fact>", "..."] } ] }

FAIL-SAFE
- If `add_observations` would target a missing entity, first issue `create_entities`.
- If lookups return nothing, fall back to `read_graph`, then proceed.
- If a tool call fails, continue the user conversation and retry later with a smaller batch.

DEFAULT USER (OVERRIDE IF KNOWN)
- Assume the primary person is `default_user` unless a different canonical ID exists in memory; if you learn it, persist it and use it thereafter.
