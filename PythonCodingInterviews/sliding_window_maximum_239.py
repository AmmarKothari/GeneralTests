from typing import *
import time
import heapq

class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        max_vals = []
        heap = []
        for i, n in enumerate(nums):
            heapq.heappush(heap, (-n, i))
            if i < (k-1):
                continue
            else:
                # Get max value
                while True:
                    x, idx = heapq.heappop(heap)
                    # Any values that are outside the window can be rejected
                    # Any value associated with an index outside the window can be removed from list
                    if idx < i-k:
                        continue
                    else:
                        # Smallest value (which is neg of largest value) will come up first always so see that before others in window.
                        max_vals.append(-x)
                        # Value was popped so add back to list
                        heapq.heappush(heap, (x, idx))
                        break


        # for idx in range(0, len(nums) - k + 1):
        #     max_vals.append(max(nums[idx:idx + k]))
        return max_vals


# Test
nums = [1, 3, -1, -3, 5, 3, 6, 7]
start = time.time()
max_vals = Solution().maxSlidingWindow(nums, 3)
assert max_vals == [3, 3, 5, 5, 6, 7]
end = time.time()
print('Time per element: {}'.format((end-start)/len(max_vals)))


nums = list(range(0, 10**5))
start = time.time()
max_vals = Solution().maxSlidingWindow(nums, 3)
end = time.time()
print('Time per element: {}'.format((end-start)/len(max_vals)))
