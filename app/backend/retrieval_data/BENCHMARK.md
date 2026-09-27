# Retrieval benchmark (fixture cards, NOT the real corpus)

Regenerate: `python app/backend/retrieval_data/benchmark.py --write`. Hit = any expected id within top-k.
Scores are the 0-1 values returned by `Retriever.retrieve` (RRF has no absolute scale).
Default constants: BM25_SCALE=16.0, HYBRID_W_BM25=0.5, cosine range 0.2-0.6, glossary terms appended for the embedder=True.
`tuned` queries were written together with the glossary and the constants were chosen on them, so they are optimistic;
`heldout` was written after the glossary was first frozen (then the glossary was extended from its misses, so it is no longer blind);
`heldout2` was written after that and is the least biased. Expect lower numbers on real cards and real speech.

### tuned: 44 in-scope + 6 out-of-scope queries

| method | recall@1 | recall@3 | recall@4 | min top score (in-scope) | max top score (out-of-scope) |
|---|---|---|---|---|---|
| bm25 | 0.955 | 1.000 | 1.000 | 0.42 (p10 0.54) | 0.68 |
| embed (plain query) | 0.682 | 0.864 | 0.886 | 0.00 (p10 0.18) | 0.36 |
| embed (+glossary terms) | 0.955 | 0.977 | 1.000 | 0.56 (p10 0.67) | 0.43 |
| hybrid (score fusion, default) | 1.000 | 1.000 | 1.000 | 0.59 (p10 0.66) | 0.51 |
| hybrid RRF (rank only) | 1.000 | 1.000 | 1.000 | n/a | n/a |

### heldout: 23 in-scope + 3 out-of-scope queries

| method | recall@1 | recall@3 | recall@4 | min top score (in-scope) | max top score (out-of-scope) |
|---|---|---|---|---|---|
| bm25 | 0.913 | 1.000 | 1.000 | 0.39 (p10 0.48) | 0.00 |
| embed (plain query) | 0.565 | 0.739 | 0.783 | 0.00 (p10 0.14) | 0.18 |
| embed (+glossary terms) | 0.870 | 1.000 | 1.000 | 0.62 (p10 0.64) | 0.17 |
| hybrid (score fusion, default) | 0.957 | 1.000 | 1.000 | 0.56 (p10 0.63) | 0.09 |
| hybrid RRF (rank only) | 0.957 | 1.000 | 1.000 | n/a | n/a |

### heldout2: 17 in-scope + 3 out-of-scope queries

| method | recall@1 | recall@3 | recall@4 | min top score (in-scope) | max top score (out-of-scope) |
|---|---|---|---|---|---|
| bm25 | 0.941 | 1.000 | 1.000 | 0.16 (p10 0.21) | 0.10 |
| embed (plain query) | 0.588 | 0.765 | 0.765 | 0.00 (p10 0.06) | 0.23 |
| embed (+glossary terms) | 0.824 | 0.941 | 0.941 | 0.18 (p10 0.24) | 0.23 |
| hybrid (score fusion, default) | 0.882 | 1.000 | 1.000 | 0.14 (p10 0.26) | 0.11 |
| hybrid RRF (rank only) | 0.882 | 1.000 | 1.000 | n/a | n/a |

### all: 84 in-scope + 12 out-of-scope queries

| method | recall@1 | recall@3 | recall@4 | min top score (in-scope) | max top score (out-of-scope) |
|---|---|---|---|---|---|
| bm25 | 0.940 | 1.000 | 1.000 | 0.16 (p10 0.46) | 0.68 |
| embed (plain query) | 0.631 | 0.810 | 0.833 | 0.00 (p10 0.14) | 0.36 |
| embed (+glossary terms) | 0.905 | 0.976 | 0.988 | 0.18 (p10 0.63) | 0.43 |
| hybrid (score fusion, default) | 0.964 | 1.000 | 1.000 | 0.14 (p10 0.61) | 0.51 |
| hybrid RRF (rank only) | 0.964 | 1.000 | 1.000 | n/a | n/a |

Default (hybrid) recall@1 by language, all in-scope queries: hi 32/32, hinglish 23/24, en 26/28

Startup (index + model load, cached vectors absent): 2.0 s.

### Snapshot on the REAL cards file (same queries; expected ids come from the planned card ids)

| method | recall@1 | recall@4 | max top score (out-of-scope) |
|---|---|---|---|
| bm25 | 0.893 | 0.988 | 0.48 |
| hybrid | 0.929 | 1.000 | 0.37 |
