# Design patterns

Tool use: the model returns a function name and arguments, the application runs the function and feeds the result back.

Agentic RAG: the model judges the quality of retrieved passages and rewrites the query or switches source instead of following one fixed path.

Planning: one concise goal is split into typed subtasks, routed to specialist agents and compiled by a coordinator.

Hand-off: each agent owns one step and passes a structured message to the next one, by rule. Group chat: agents post into a shared channel managed by a coordinator. Collaborative filtering: specialists answer in parallel and an aggregator reconciles.

Metacognition: plan, act, evaluate, adjust. The agent changes its own strategy when feedback says the last choice was bad.
