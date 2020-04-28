from typing import *
import util


# class Solution:
#     def calculateMinimumHP(self, dungeon: List[List[int]]) -> int:
#         _, min_hp_along_path = self.calc_min_hp_core(dungeon)
#         return max(-min_hp_along_path + 1, 1)
#
#     def calc_min_hp_core(self, dungeon: List[List[int]]) -> Tuple[int, int]:
#         current_cell_val = dungeon[0][0]
#         if len(dungeon) == 1 and len(dungeon[0]) == 1:
#             # Princess cell (bottom right) so return value
#             min_hp_along_path = current_cell_val
#             return current_cell_val, min_hp_along_path
#
#         if len(dungeon) > 1:
#             move_down_remaining_dungeon = dungeon[1:]
#             hp_down, min_hp_along_path_down = self.calc_min_hp_core(move_down_remaining_dungeon)
#         else:
#             hp_down = min_hp_along_path_down = None
#         if len(dungeon[0]) > 1:
#             move_right_remaining_dungeon = [row[1:] for row in dungeon]
#             hp_right, min_hp_along_path_right = self.calc_min_hp_core(move_right_remaining_dungeon)
#         else:
#             hp_right = min_hp_along_path_right = None
#
#         if min_hp_along_path_right is not None and min_hp_along_path_down is None:
#             current_hp = hp_right + current_cell_val
#             min_hp_along_path = min(current_hp, min_hp_along_path_right)
#         elif min_hp_along_path_right is None and min_hp_along_path_down is not None:
#             current_hp = hp_down + current_cell_val
#             min_hp_along_path = min(current_hp, min_hp_along_path_down)
#         else:
#             if min_hp_along_path_down > min_hp_along_path_right:
#                 current_hp = hp_down + current_cell_val
#                 min_hp_along_path = min(current_hp, min_hp_along_path_down)
#             else:
#                 current_hp = hp_right + current_cell_val
#                 min_hp_along_path = min(current_hp, min_hp_along_path_right)
#         return current_hp, min_hp_along_path

class Solution:
    def calculateMinimumHP(self, dungeon):
        # Flipping the signs to align with HP needed idea
        m = len(dungeon)
        n = len(dungeon[0])
        # Use dict indexed by tuple of grid indices to store path calc
        # Know the min hp needed to reach the last cell from the last cell is the last cell value
        solution_grid = {(m - 1, n - 1): max(1, -dungeon[-1][-1] + 1)}

        def get_min_hp_required(x, y):
            # When index is out of bounds return really large value?
            if x >= m or y >= n:
                return float('inf')
            # Calculate value of cell if it doesn't exist
            if (x, y) not in solution_grid:
                # Take the minimum of the future path.  HP required for this step includes current cell so subtact that
                solution_grid[(x, y)] = min(get_min_hp_required(x + 1, y), get_min_hp_required(x, y + 1)) - dungeon[x][
                    y]
                # HP can be removed so check to see if a lower HP limit is needed.
                if dungeon[x][y] > 0:
                    solution_grid[(x, y)] = max(1, solution_grid[x, y])
            print((x, y, solution_grid))
            return solution_grid[(x, y)]
        return get_min_hp_required(0, 0)


# Test
dungeon = [[-2, -3, 3], [-5, -10, 1], [10, 30, -5]]
min_hp_required = Solution().calculateMinimumHP(dungeon)
import pdb; pdb.set_trace()
assert min_hp_required == 7

dungeon = [[100]]
min_hp_required = Solution().calculateMinimumHP(dungeon)
assert min_hp_required == 1

# dungeon = [[10, 10, 3], [-5, -10, 1], [10, 30, -5]]
# min_hp_required = Solution().calculateMinimumHP(dungeon)
# assert min_hp_required == 7

dungeon = [[0, 0]]
min_hp_required = Solution().calculateMinimumHP(dungeon)
assert min_hp_required == 1
