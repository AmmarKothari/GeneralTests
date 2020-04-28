#include <iostream>
#include <assert.h>

class Solution {
public:
    int getSum(int a, int b) {
        return a + b;
    }
};

int main(int argc, const char * argv[]) {
    Solution sol;
    // Test
    int res = sol.getSum(1, 2);
    std::cout << res << std::endl;
    assert (res == 3);
}