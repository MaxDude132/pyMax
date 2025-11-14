"""Memory management tests to ensure structural sharing and efficient memory usage."""

import tracemalloc
from tests.main import run_source


def measure_memory_usage(code):
    """Measure peak memory usage while executing code."""
    tracemalloc.start()
    print(run_source(code))
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def test_memory_shared_base_data():
    """Verify that multiple derived lists share the same base data in memory."""
    code_base = """
base = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
"""

    code_many_branches = """
base = List()
for i in List(1,2,3,4,5,6,7,8,9,10) {
    for j in List(1,2,3,4,5,6,7,8,9,10) {
        base = base.push(i)
    }
}
print(base.length())
"""
    code_multiple_lists = """
base = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
base = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
base = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
base = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
base = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
base = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
base = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
"""

    base_memory = measure_memory_usage(code_base)
    branches_memory = measure_memory_usage(code_many_branches)
    multiple_lists_memory = measure_memory_usage(code_multiple_lists)

    # With structural sharing, 10 branches should NOT use 10x the memory
    # Allow up to 2x for reasonable overhead
    assert branches_memory < base_memory * 2, (
        f"Memory not shared efficiently: base={base_memory}, "
        f"10 branches={branches_memory}. Expected < {base_memory * 2}"
    )
    # Two separate lists should use roughly double the memory of one
    assert branches_memory < multiple_lists_memory, (
        "Memory for multiple lists not greater than branches: "
        f"branches={branches_memory}, multiple lists={multiple_lists_memory}."
    )


def test_memory_set_modification_minimal():
    """Verify that set() doesn't duplicate the entire list in memory."""
    code_no_set = """
original = List()
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        original = original.push(num)
    }
}
print("done")
"""

    code_with_set = """
original = List()
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        original = original.push(num)
    }
}
modified = original.set(50, 999)
print("done")
"""

    mem_no_set = measure_memory_usage(code_no_set)
    mem_with_set = measure_memory_usage(code_with_set)

    # set() should only add minimal memory for the modification
    # Not double the memory (full copy)
    assert mem_with_set < mem_no_set * 1.3, (
        f"Set() duplicated too much memory: no_set={mem_no_set}, "
        f"with_set={mem_with_set}. Expected < {mem_no_set * 1.3}"
    )


def test_memory_push_chain_efficient():
    """Verify that a chain of pushes doesn't linearly increase memory."""
    code_10_pushes = """
list = List(1, 2, 3, 4, 5)
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    list = list.push(num)
}
print("done")
"""

    code_100_pushes = """
list = List(1, 2, 3, 4, 5)
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        list = list.push(num)
    }
}
print("done")
"""

    mem_10 = measure_memory_usage(code_10_pushes)
    mem_100 = measure_memory_usage(code_100_pushes)

    # 100 pushes vs 10 pushes
    # Items: 105 vs 15 = 7x
    # With compaction, memory ratio should be roughly proportional to item count
    ratio = mem_100 / mem_10 if mem_10 > 0 else float("inf")

    # Allow up to 10x (should be closer to 7x with good compaction)
    assert ratio < 10, (
        f"Memory grew too much with push chain: 10 pushes={mem_10}, "
        f"100 pushes={mem_100}, ratio={ratio:.2f}. Expected ratio < 10"
    )


def test_memory_compaction_reduces_overhead():
    """Verify that compaction actually reduces memory overhead."""
    # Without compaction - short chain
    code_short = """
list = List(1)
for num in List(0, 1, 2, 3, 4) {
    list = list.push(num)
}
print("done")
"""

    # With compaction - long chain that triggers compaction
    code_long = """
list = List(1)
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19) {
    list = list.push(num)
}
print("done")
"""

    mem_short = measure_memory_usage(code_short)
    mem_long = measure_memory_usage(code_long)

    # 21 items vs 6 items = 3.5x
    # Memory should be roughly proportional (with compaction)
    ratio = mem_long / mem_short if mem_short > 0 else float("inf")

    # Should be less than 5x (would be much higher without compaction)
    assert ratio < 5, (
        f"Compaction didn't reduce overhead: short={mem_short}, long={mem_long}, "
        f"ratio={ratio:.2f}. Expected ratio < 5"
    )


def test_memory_map_structural_sharing():
    """Verify that maps use structural sharing efficiently."""
    code_base = """
base = Map(1 -> "a", 2 -> "b", 3 -> "c", 4 -> "d", 5 -> "e")
print("done")
"""

    code_derived = """
base = Map(1 -> "a", 2 -> "b", 3 -> "c", 4 -> "d", 5 -> "e")
d1 = base.push(6 -> "f")
d2 = base.push(7 -> "g")
d3 = base.push(8 -> "h")
print("done")
"""

    base_memory = measure_memory_usage(code_base)
    derived_memory = measure_memory_usage(code_derived)

    # d3 should share base data, only adding minimal memory
    assert derived_memory < base_memory * 2, (
        f"Map not sharing structure: base={base_memory}, derived={derived_memory}. "
        f"Expected derived < {base_memory * 2}"
    )


def test_memory_branching_from_same_base():
    """Verify that multiple branches from same base don't multiply memory."""
    code_single = """
base = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
branch = base.push(99)
print("done")
"""

    code_many = """
base = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
b1 = base.push(91)
b2 = base.push(92)
b3 = base.push(93)
b4 = base.push(94)
b5 = base.push(95)
b6 = base.push(96)
b7 = base.push(97)
b8 = base.push(98)
b9 = base.push(99)
b10 = base.push(100)
print("done")
"""

    single_memory = measure_memory_usage(code_single)
    many_memory = measure_memory_usage(code_many)

    # 10 branches shouldn't use 10x memory due to sharing
    assert many_memory < single_memory * 3, (
        f"Multiple branches from same base using too much memory: "
        f"single branch={single_memory}, 10 branches={many_memory}. "
        f"Expected < {single_memory * 3}"
    )


def test_memory_deep_nesting_with_compaction():
    """Verify that deep chains compact and don't accumulate excess memory."""
    code_shallow = """
list = List(1, 2, 3, 4, 5)
list = list.push(6)
list = list.push(7)
list = list.push(8)
print("done")
"""

    code_deep = """
list = List(1, 2, 3, 4, 5)
-- Create 20 pushes to trigger compaction
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19) {
    list = list.push(num)
}
print("done")
"""

    shallow_memory = measure_memory_usage(code_shallow)
    deep_memory = measure_memory_usage(code_deep)

    # 25 items vs 8 items = ~3x
    ratio = deep_memory / shallow_memory if shallow_memory > 0 else float("inf")

    # With compaction, ratio should be reasonable
    assert ratio < 5, (
        f"Deep chain accumulated too much overhead: shallow={shallow_memory}, "
        f"deep={deep_memory}, ratio={ratio:.2f}. Expected ratio < 5"
    )


def test_memory_no_duplication_on_read():
    """Verify that reading/accessing values doesn't increase memory."""
    code_before = """
list = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
print("done")
"""

    code_after = """
list = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val1 = list.get(0)
val2 = list.get(1)
val3 = list.get(2)
val4 = list.get(3)
val5 = list.get(4)
print("done")
"""

    before_memory = measure_memory_usage(code_before)
    after_memory = measure_memory_usage(code_after)

    # Reading should add minimal memory (just the variables)
    # Allow for variable overhead but shouldn't duplicate list
    assert after_memory < before_memory * 1.2, (
        f"Reading values increased memory significantly: before={before_memory}, "
        f"after={after_memory}. Expected < {before_memory * 1.2}"
    )
