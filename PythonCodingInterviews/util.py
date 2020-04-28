class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

    def __repr__(self):
        return 'Node Value: {}'.format(self.val)


def get_list_node(nums):
    nodes = [ListNode(num) for num in nums]
    for idx, node in enumerate(nodes[:-1]):
        node.next = nodes[idx + 1]
    return nodes


def assert_list_order(head, order):
    i = 0
    while head:
        assert head.val == order[i], 'Expected: {}, Actual: {}'.format(order[i], head.val)
        i += 1
        head = head.next


class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

    def __repr__(self):
        if self.left and self.right:
            return 'Node Value: {}, Left: {}, Right: {}'.format(self.val, self.left.val, self.right.val)
        else:
            return 'Node Value: {}, Left: {}, Right: {}'.format(self.val, self.left, self.right)


def get_tree(nums):
    root = TreeNode(nums[0])
    root, _ = build_remaining_tree(root, nums[1:])
    return root


def build_remaining_tree(node, nums):
    if nums[0]:
        node.left = TreeNode(nums[0])
    if nums[1]:
        node.right = TreeNode(nums[1])
    remaining_nums = nums[2:]
    if len(remaining_nums) != 0:
        if node.left and node.left.val:
            node.left, remaining_nums = build_remaining_tree(node.left, remaining_nums)
        if node.right and node.right.val:
            node.right, nums = build_remaining_tree(node.right, remaining_nums)
    return node, remaining_nums
