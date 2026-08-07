# Collaboration Boundary

`skill-pandadata-api` supplies versioned API contracts. Existing factor evaluation, IC, and backtest Skills may consume this Skill's output. No collaborator is a hard local runtime dependency.

This Skill owns graph construction, fixed channel normalization, graph filtering, and diagnostics. It does not copy data access, model training, evaluation, or portfolio implementation. Missing collaborator evidence remains `not_checked` or blocked.
