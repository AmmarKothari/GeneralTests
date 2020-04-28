#include <vector>
#include <string>
#include <set>
#include <iostream>
#include <queue>
#include <assert.h>

using namespace std;

//function to print the queue
void printQueue(queue<int> q)
{
	//printing content of queue 
	while (!q.empty()){
		cout<<" "<<q.front();
		q.pop();
	}
	cout<<endl;
}

class Solution
{
public:
    int subarraySum(vector<int> &nums, int k)
    {
        int sol = 0, running_sum = 0;
        queue<int> sub_array;
        for (auto v : nums)
        {
            // add value to subarray
            sub_array.push(v);
            // add to total
            running_sum += v;
            // if greater than value, remove last value and reduce running sum
            if (running_sum > k)
            {
                while (sub_array.size() > 1 and running_sum > k){
                    running_sum -= sub_array.front();
                    sub_array.pop();
                    cout << "Running Sum in sub loop: " << running_sum << endl;
                }
            }
            // if equal value, increment counter
            if (running_sum == k)
            {
                sol++;
            }
            cout << "Array Value: " << v << endl;
            cout << "Running Sum: " << running_sum << endl;
            cout << "Solution counter: " << sol << endl;
            printQueue(sub_array);
        }
        return sol;
    }
};

int main()
{
    Solution sol;
    int k, output;

    // Tests
    vector<int> nums{1, 1, 1};
    k = 2;
    output = sol.subarraySum(nums, k);
    assert(output==2);
    cout << "Test 1 Passes" << endl << endl;

    // Tests
    vector<int> nums2{-1, -1, 1};
    k =0;
    output = sol.subarraySum(nums2, k);
    assert(output==1);
}