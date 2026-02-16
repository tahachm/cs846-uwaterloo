# A2. K-th Smallest Value on a Tree Path (with Updates)

You are given a connected undirected tree with `n` nodes labeled `0..n-1`. Node `i` has value `values[i]`.

Process queries:

- `('U', u, x)`: set `values[u] = x`
- `('Q', u, v, k)`: return the **k-th smallest** value on the simple path from `u` to `v` (inclusive)

Return answers for all `('Q', ...)` queries in order. `k` is **1-indexed**.

## Function

```python
class Solution:
    def processQueries(self, n, edges, values, queries):
        """Return answers to all 'Q' queries."""
```

## Example

```text
n = 5
edges = [(0,1), (1,2), (1,3), (3,4)]
values = [5, 1, 7, 3, 9]
queries = [('Q',2,4,2), ('U',1,8), ('Q',0,2,2), ('Q',4,4,1)]
output = [3, 7, 9]
```

## Constraints

- `edges` has length `n-1` and forms a tree
- For each `('Q', u, v, k)`: `1 <= k <= (#nodes on path u..v)`

## Unit tests

Tests: `<path-to-dir>/test_a2_kth_smallest_path.py`.

You **must** specify which implementation file(s) to test using `A2_IMPLS`.

```bash
A2_IMPLS=A2_kth_smallest_path_solution.py \
  python3 -m unittest discover -s <path-to-dir> -p 'test_a2_kth_smallest_path.py' -v
```
