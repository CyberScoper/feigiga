#!/usr/bin/env python3
"""Независимое решение prime-maze: свой Miller-Rabin (без sympy)."""
import json
from collections import defaultdict


# --- Miller-Rabin, детерминированный для n < 3.317e14 ---
# Witnesses: [2,3,5,7,11,13,17,19,23,29,31,37] — детерминирован для n < 3.317*10^14
_WITNESSES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    # маленькие простые
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n == p:
            return True
        if n % p == 0:
            return False
    # n - 1 = d * 2^r
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in _WITNESSES:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True


# --- Самопроверка Miller-Rabin ---
def _self_check():
    # известные простые
    known_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 97, 101, 7919,
                    104729, 1000003, 1000000007, 1000000009,
                    9999999967, 99999999977,
                    999999999989, 9999999999971, 99999999999973]
    # известные составные
    known_composites = [1, 4, 6, 8, 9, 15, 21, 25, 100, 561, 1105, 1729, 2465,
                        2821, 6601, 8911, 10585,  # числа Кармайкла
                        9999999967 * 2, 1000000007 * 1000000009]
    for p in known_primes:
        assert is_prime(p), f"FAIL: {p} should be prime"
    for c in known_composites:
        assert not is_prime(c), f"FAIL: {c} should be composite"
    print("[self-check] Miller-Rabin OK")


def main():
    _self_check()

    with open('/mnt/extra/vibe/scratch/prime-maze/maze.json') as f:
        data = json.load(f)

    nodes = {n['id']: n['letter'] for n in data['nodes']}
    print(f"nodes: {len(nodes)}  edges: {len(data['edges'])}")

    # adjacency: from -> sorted list (desc by number) of (to, number)
    adj = defaultdict(list)
    for e in data['edges']:
        adj[e['from']].append((e['to'], e['number']))
    for k in adj:
        adj[k].sort(key=lambda x: -x[1])

    # M-узлы
    m_nodes = sorted([nid for nid, ltr in nodes.items() if ltr == 'M'])
    print(f"M-nodes: {len(m_nodes)}")

    # кеш проверки простоты
    prime_cache = {}
    def is_p(n):
        if n not in prime_cache:
            prime_cache[n] = is_prime(n)
        return prime_cache[n]

    results = []
    for start in m_nodes:
        word = []
        path_ids = []
        cur = start
        visited = set()
        cycled = False
        while True:
            word.append(nodes[cur])
            path_ids.append(cur)
            if cur in visited:
                cycled = True
                break
            visited.add(cur)
            # найти первое простое в отсортированных по убыванию рёбрах
            nxt = None
            for to, num in adj.get(cur, []):
                if is_p(num):
                    nxt = to
                    break
            if nxt is None:
                break
            cur = nxt
        results.append({
            'start': start,
            'word': ''.join(word),
            'len': len(word),
            'path_ids': path_ids,
            'cycled': cycled,
        })

    # отчёт
    print("\n=== Все 24 пути ===")
    for r in sorted(results, key=lambda x: -x['len']):
        marker = " [CYCLE!]" if r['cycled'] else ""
        print(f"{r['start']}  len={r['len']:3d}  {r['word']}{marker}")

    # кандидат: самое длинное некруговое слово (или просто самое длинное)
    print("\n=== Кандидаты ===")
    non_cycled = [r for r in results if not r['cycled']]
    if non_cycled:
        best = max(non_cycled, key=lambda x: x['len'])
        print(f"Самый длинный без цикла: {best['start']} len={best['len']}")
        print(f"  слово: {best['word']}")
    cycled_results = [r for r in results if r['cycled']]
    if cycled_results:
        print(f"С циклами: {len(cycled_results)}")

    # Если все одинаковые — это и есть ответ
    words = set(r['word'] for r in results)
    print(f"\nУникальных слов: {len(words)}")
    if len(words) == 1:
        ans = list(words)[0]
        print(f"\n=== ФИНАЛ ===\n{ans}")
    else:
        # Все ли начинаются одинаково? Какое самое длинное?
        longest = max(results, key=lambda x: x['len'])
        print(f"\n=== ФИНАЛ (самый длинный) ===\n{longest['word']}")


if __name__ == '__main__':
    main()
