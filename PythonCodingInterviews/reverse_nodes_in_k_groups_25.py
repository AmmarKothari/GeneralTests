import util
from util import ListNode


class Solution:
    def reverseKGroup(self, head: ListNode, k: int) -> ListNode:
        if not head:
            return head
        node_tracker = []  # Holds nodes in order from original list
        node = head
        for i in range(k):
            if node:
                node_tracker.append(node)
                node = node.next
            else:
                # Less than K linked nodes so just return original
                return head
        next_node = self.reverseKGroup(node_tracker[-1].next, k)
        node_tracker.reverse()
        previous_node = node_tracker[0]
        # import pdb; pdb.set_trace()
        for node in node_tracker[1:]:
            previous_node.next = node
            previous_node = node
        previous_node.next = next_node
        return node_tracker[0]


# Tests
# nums = range(1, 3)
# node_list = util.get_list_node(nums)
# sol = Solution().reverseKGroup(node_list[0], 2)
# util.assert_list_order(sol, [2, 1])
#
#
# nums = range(1, 5)
# node_list = util.get_list_node(nums)
# sol = Solution().reverseKGroup(node_list[0], 2)
# util.assert_list_order(sol, [2, 1, 4, 3])


nums = range(1, 6)
node_list = util.get_list_node(nums)
sol = Solution().reverseKGroup(node_list[0], 2)
util.assert_list_order(sol, [2, 1, 4, 3, 5])

node_list = util.get_list_node(nums)
sol = Solution().reverseKGroup(node_list[0], 3)
util.assert_list_order(sol, [3, 2, 1, 4, 5])
