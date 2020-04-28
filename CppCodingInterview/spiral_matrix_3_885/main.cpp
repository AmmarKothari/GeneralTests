#include <vector>
#include <string>
#include <set>
#include <iostream>

using namespace std;

void print_vector(vector<vector<int>> vec){
    for (auto cell: vec){
        for (auto v: cell){
            cout << v << ",";
        }
        cout << endl;
    }
}

class Solution {
public:
    bool within_bounds(vector<int> index, int R, int C){
        return (index[0] < R and index[0] >= 0 and index[1] < C and index[1] >= 0);
    };

    void check_and_update_sol(vector<int> index, int R, int C, vector<vector<int>> &sol){
        if (within_bounds(index, R, C)){
            sol.push_back(index);
            cout << index[0] << ", " << index[1] << endl;
        }
        else{
            cout << "Skipped Index: " << index[0] << ", " << index[1] << endl;
        }
    }

    vector<vector<int>> spiralMatrixIII(int R, int C, int r0, int c0) {
        vector<vector<int>> sol;
        vector<int> index, prev_index;
        index.push_back(r0);
        index.push_back(c0);
        sol.push_back(index);
        int vec_len = 1;
        int iteration_direction = 1;
        prev_index = sol.back();
        while (sol.size() < R*C){
            // iterate along columns
            for (int c=1; c<=vec_len; c++){
                index.clear();
                index.push_back(prev_index[0]);
                index.push_back(prev_index[1] + iteration_direction);
                check_and_update_sol(index, R, C, sol);
                prev_index = index;
            }
            // iterate forward along rows
            for (int r=1; r<=vec_len; r++){
                index.clear();
                index.push_back(prev_index[0] + iteration_direction);
                index.push_back(prev_index[1]);
                check_and_update_sol(index, R, C, sol);
                prev_index = index;
            }
            // Update vec_len for the next iteration
            vec_len += 1;
            iteration_direction *= -1;
        }
        return sol;
    }
};

int main(){
    Solution sol;
    vector<vector<int>> output;

    // Tests
    output = sol.spiralMatrixIII(1, 4, 0, 0);
    print_vector(output);


    // Tests
    output = sol.spiralMatrixIII(5, 6, 1, 4);
    print_vector(output);
}