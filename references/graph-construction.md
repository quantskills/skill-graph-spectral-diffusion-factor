# Graph Construction

Nodes are T-day eligible stocks. The primary layer connects stocks sharing a versioned industry classification. Optional concept edges use a predeclared coefficient and point-in-time membership snapshot. Duplicate undirected edges are merged; self-loops and nonpositive weights are removed.

The normalized operator is `S = D^(-1/2) A D^(-1/2)`. Zero-degree nodes are retained in diagnostics but cannot receive graph-derived factor values.

Correlation edges are diagnostic in v1. If enabled later, they must use `< T` returns, a frozen window/threshold/max-degree rule, and a separate fingerprint.
