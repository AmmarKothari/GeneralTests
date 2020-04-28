class Solution:
    def longestDecomposition(self, text: str) -> int:
        i = 0
        decomposition_counter = 0
        while True:
            if len(text) == 0:
                break
            if text[:i] == text[-i:]:
                # Update count
                decomposition_counter += 2
                # Remove matching text from string
                sub_string = text[i:-i]
                # Call longestdecomp on substring
                decomposition_counter += self.longestDecomposition(sub_string)
                break
            i += 1
            if i > len(text) // 2:
                decomposition_counter += 1
                break
        return decomposition_counter


# Test
text = "merchant"
sol = Solution().longestDecomposition(text)
assert sol == 1

text = "ghiabcdefhelloadamhelloabcdefghi"
sol = Solution().longestDecomposition(text)
assert sol == 7

text = "antaprezatepzapreanta"
sol = Solution().longestDecomposition(text)
assert sol == 11

text = "aaa"
sol = Solution().longestDecomposition(text)
assert sol == 3

text = "elvtoelvto"
sol = Solution().longestDecomposition(text)
assert sol == 2