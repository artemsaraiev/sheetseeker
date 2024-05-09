# from .add_function import add
# import pytest

# def test_add_positive_numbers():
#     assert add(1, 2) == 3

# def test_add_negative_numbers():
#     assert add(-1, -2) == -3

# def test_add_mixed_numbers():
#     print(5)
#     assert add(1, -2) == 2

# def jaccard_similarity(set1, set2):
#     intersection = len(set1.intersection(set2))
#     union = len(set1.union(set2))
#     return intersection / union if union != 0 else 0

# # Example function to test
# def generate_set():
#     return {1, 2, 3, 4, 5}

# # Test function
# def test_similarity():
#     expected_set = {1, 3, 5, 7, 9}  # Example expected set
#     generated_set = generate_set()
#     similarity = jaccard_similarity(expected_set, generated_set)
#     assert similarity == pytest.approx(0.6, abs=1e-2)  # Check similarity percentage