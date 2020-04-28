import util
from util import TreeNode


class Solution:
    def maxPathSum(self, root: TreeNode) -> int:
        if not root:
            return 0
        self.max_sum = -float('inf')

        def depth_first_search(node):
            if not node:
                # Some nodes are None (to indicate no more tree) so return 0 here so we can max over it.
                return 0
            left_max_sum = depth_first_search(node.left)
            right_max_sum = depth_first_search(node.right)
            # The best path is to follow the max left path, through the root, then through the max right path
            # or the best path is elsewhere in the tree
            self.max_sum = max(self.max_sum, node.val + left_max_sum + right_max_sum)
            # Return a value only if its greater than 0 (because best path is no path at all?)
            return max(node.val + max(left_max_sum, right_max_sum), 0)

        depth_first_search(root)
        return self.max_sum


# Tests
nums = [1, 2, 3]
tree = util.get_tree(nums)
max_val = Solution().maxPathSum(tree)
assert max_val == 6

nums = [-1, -2, -3, 100, 0, None, None, None, None, 0, 100]
tree = util.get_tree(nums)
max_val = Solution().maxPathSum(tree)
import pdb;

pdb.set_trace()
assert max_val == 0

nums = [-10, 9, 20, None, None, 15, 7]
tree = util.get_tree(nums)
max_val = Solution().maxPathSum(tree)
assert max_val == 42
