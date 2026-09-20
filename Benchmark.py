"""
Hard Reasoning Benchmark for LLMs

The model must solve multiple independent reasoning tasks involving:
- Constraint satisfaction
- Scheduling
- Graph reasoning
- Probability
- State transitions
- Combinatorics
- Deduction
- Optimization
- Adversarial edge cases

The benchmark is intentionally designed so that guessing is difficult.
"""

from itertools import permutations, combinations
from collections import defaultdict, deque
from fractions import Fraction


# ============================================================
# 1. CONSTRAINT SATISFACTION
# ============================================================

def problem_1():
    """
    Five people: A, B, C, D, E.
    Five positions: 1..5.

    Rules:
      A is immediately before C.
      B is not in position 1 or 5.
      D is somewhere after B.
      E is not next to A.
      C is not in position 5.

    Find the unique valid ordering.
    """

    people = "ABCDE"
    solutions = []

    for p in permutations(people):
        pos = {x: p.index(x) + 1 for x in people}

        if pos["C"] != pos["A"] + 1:
            continue
        if pos["B"] in (1, 5):
            continue
        if pos["D"] <= pos["B"]:
            continue
        if abs(pos["E"] - pos["A"]) == 1:
            continue
        if pos["C"] == 5:
            continue

        solutions.append("".join(p))

    return solutions


# ============================================================
# 2. SCHEDULING
# ============================================================

def problem_2():
    """
    Six tasks A-F must be scheduled in six slots.

    Constraints:
      A occurs before D.
      B occurs immediately before E.
      C cannot be first or last.
      F occurs after D.
      A is not adjacent to C.
      E occurs before F.

    Return every valid schedule.
    """

    tasks = "ABCDEF"
    solutions = []

    for p in permutations(tasks):
        pos = {x: p.index(x) for x in tasks}

        if not pos["A"] < pos["D"]:
            continue
        if pos["E"] != pos["B"] + 1:
            continue
        if pos["C"] in (0, 5):
            continue
        if not pos["D"] < pos["F"]:
            continue
        if abs(pos["A"] - pos["C"]) == 1:
            continue
        if not pos["E"] < pos["F"]:
            continue

        solutions.append("".join(p))

    return solutions


# ============================================================
# 3. GRAPH REASONING
# ============================================================

def problem_3():
    """
    Directed graph.

    A -> B
    A -> C
    B -> D
    C -> D
    C -> E
    D -> F
    E -> F
    F -> G

    Question:
    How many distinct directed paths exist from A to G?
    """

    graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D", "E"],
        "D": ["F"],
        "E": ["F"],
        "F": ["G"],
        "G": []
    }

    memo = {}

    def count_paths(node):
        if node == "G":
            return 1

        if node in memo:
            return memo[node]

        total = sum(count_paths(n) for n in graph[node])
        memo[node] = total
        return total

    return count_paths("A")


# ============================================================
# 4. PROBABILITY
# ============================================================

def problem_4():
    """
    A box contains:
      5 red balls
      4 blue balls
      3 green balls

    Three balls are drawn without replacement.

    What is the probability that:
      - exactly two colors appear
      - and red appears at least once?

    Return the answer as an exact Fraction.
    """

    total = 12
    total_ways = 0
    valid = 0

    # enumerate color counts
    for r in range(4):
        for b in range(4):
            for g in range(4):
                if r + b + g != 3:
                    continue
                if r > 5 or b > 4 or g > 3:
                    continue

                ways = (
                    __import__("math").comb(5, r)
                    * __import__("math").comb(4, b)
                    * __import__("math").comb(3, g)
                )

                total_ways += ways

                colors = sum(x > 0 for x in (r, b, g))

                if colors == 2 and r >= 1:
                    valid += ways

    return Fraction(valid, total_ways)


# ============================================================
# 5. STATE TRANSITION
# ============================================================

def problem_5():
    """
    A machine has state (x, y).

    Initial state:
        (2, 3)

    Operations:

        P:
            x = x + y
            y = y - 1

        Q:
            x = x - 2
            y = x + y
            IMPORTANT: y uses the OLD value of x.

        R:
            swap(x, y)

    Apply:

        P, R, Q, P, Q, R, P

    Return the final state.
    """

    x, y = 2, 3

    # P
    x, y = x + y, y - 1

    # R
    x, y = y, x

    # Q
    old_x = x
    x = x - 2
    y = old_x + y

    # P
    x, y = x + y, y - 1

    # Q
    old_x = x
    x = x - 2
    y = old_x + y

    # R
    x, y = y, x

    # P
    x, y = x + y, y - 1

    return x, y


# ============================================================
# 6. OPTIMIZATION / KNAPSACK
# ============================================================

def problem_6():
    """
    Choose a subset of projects.

    Each project has (cost, value):

        A = (4, 7)
        B = (6, 10)
        C = (5, 9)
        D = (7, 13)
        E = (3, 5)
        F = (8, 15)

    Budget = 18

    Find:
      1. Maximum possible value.
      2. Lexicographically smallest set among all optimal sets.
    """

    projects = {
        "A": (4, 7),
        "B": (6, 10),
        "C": (5, 9),
        "D": (7, 13),
        "E": (3, 5),
        "F": (8, 15),
    }

    best_value = -1
    best_sets = []

    names = sorted(projects)

    for r in range(len(names) + 1):
        for subset in combinations(names, r):

            cost = sum(projects[x][0] for x in subset)
            value = sum(projects[x][1] for x in subset)

            if cost > 18:
                continue

            if value > best_value:
                best_value = value
                best_sets = [subset]

            elif value == best_value:
                best_sets.append(subset)

    best_sets.sort()

    return best_value, best_sets[0]


# ============================================================
# 7. LOGICAL DEDUCTION
# ============================================================

def problem_7():
    """
    Four people: Alice, Bob, Carol, David.

    Exactly one person is lying.

    Statements:

      Alice: "Bob is lying."
      Bob: "Carol is lying."
      Carol: "David is lying."
      David: "Bob is telling the truth."

    Determine who is lying.
    """

    people = ["Alice", "Bob", "Carol", "David"]

    # Try each person as the unique liar.
    valid = []

    for liar in people:

        truth = {
            p: (p != liar)
            for p in people
        }

        statements = {
            "Alice": truth["Bob"] is False,
            "Bob": truth["Carol"] is False,
            "Carol": truth["David"] is False,
            "David": truth["Bob"] is True,
        }

        if all(statements[p] == truth[p] for p in people):
            valid.append(liar)

    return valid


# ============================================================
# 8. COMBINATORICS
# ============================================================

def problem_8():
    """
    How many 6-character strings can be created from:

        A B C D E F G

    without repetition, such that:

      - A and B are both present or both absent.
      - C appears before D.
      - E cannot be adjacent to F.
      - The string starts with a vowel.
        (A and E are vowels.)

    Return the exact count.
    """

    chars = "ABCDEFG"
    count = 0

    for p in permutations(chars, 6):

        s = "".join(p)

        if ("A" in s) != ("B" in s):
            continue

        if "C" in s and "D" in s:
            if s.index("C") > s.index("D"):
                continue
        else:
            continue

        if "E" in s and "F" in s:
            if abs(s.index("E") - s.index("F")) == 1:
                continue

        if s[0] not in "AE":
            continue

        count += 1

    return count


# ============================================================
# 9. ADVERSARIAL REASONING
# ============================================================

def problem_9():
    """
    Consider this Python-like operation:

        x = [1, 2, 3]
        y = x
        z = x[:]

        x.append(4)
        y[0] = 99
        z.append(5)

    What are the final values of x, y, z?

    Return them exactly.
    """

    x = [1, 2, 3]
    y = x
    z = x[:]

    x.append(4)
    y[0] = 99
    z.append(5)

    return x, y, z


# ============================================================
# 10. INVARIANT REASONING
# ============================================================

def problem_10():
    """
    Start with integer n = 7.

    Repeatedly apply:

        if n is even:
            n = n / 2
        else:
            n = 3*n + 1

    Stop when n reaches 1.

    Return the number of transformations performed.
    """

    n = 7
    steps = 0

    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1

        steps += 1

    return steps


# ============================================================
# 11. SET LOGIC
# ============================================================

def problem_11():
    """
    There are 100 students.

    60 know Python.
    45 know JavaScript.
    30 know SQL.

    25 know both Python and JavaScript.
    18 know both Python and SQL.
    12 know both JavaScript and SQL.
    8 know all three.

    How many students know at least one of the three?
    """

    result = (
        60
        + 45
        + 30
        - 25
        - 18
        - 12
        + 8
    )

    return result


# ============================================================
# 12. META REASONING
# ============================================================

def problem_12():
    """
    Three boxes are labeled:

        BOX A: "Gold"
        BOX B: "Silver"
        BOX C: "Gold + Silver"

    Every label is WRONG.

    Each box contains either:
        - only gold
        - only silver
        - both gold and silver

    You may draw exactly ONE item from exactly ONE box.

    Which box must you draw from to determine the contents
    of all three boxes?

    Return the box name and explain why.
    """

    return "BOX C"


# ============================================================
# BENCHMARK
# ============================================================

def run_benchmark():
    expected = {
        1: problem_1(),
        2: problem_2(),
        3: problem_3(),
        4: problem_4(),
        5: problem_5(),
        6: problem_6(),
        7: problem_7(),
        8: problem_8(),
        9: problem_9(),
        10: problem_10(),
        11: problem_11(),
        12: problem_12(),
    }

    print("=" * 70)
    print("HARD LLM REASONING BENCHMARK")
    print("=" * 70)

    for i, answer in expected.items():
        print(f"\nProblem {i}")
        print("-" * 30)
        print(answer)

    print("\n" + "=" * 70)
    print("Benchmark complete.")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
