#include <iostream>
#include <assert.h>
#include "tree.cpp"
#include <vector>

using namespace std;

class Solution {
public:
    bool should_delete_current_val(TreeNode* root, vector<int>& to_delete){
        for (auto v: to_delete){
            if (root->val == v){
                return true;
            }
        }
        return false;
    }
    vector<TreeNode*> delNodes(TreeNode* root, vector<int>& to_delete) {
        vector<TreeNode*> forest;
        forest = delNodes_helper(root, to_delete);
        // Root of original tree should be added to the forest.
        if (!should_delete_current_val(root, to_delete)){
            forest.push_back(root);
        }
        // Remove any values that are in the forest
        bool should_clean = true;
        vector<TreeNode*> cleaned_forest, additional_forest;
        if (forest.size() > 0){
            print_forest(forest);
        }
        while (should_clean){
            cleaned_forest.clear();
            should_clean = false;
            for (auto node: forest){
                if(should_delete_current_val(node, to_delete)){
                    additional_forest.clear();
                    additional_forest = delNodes_helper(node, to_delete);
                    cleaned_forest.insert(cleaned_forest.end(), additional_forest.begin(), additional_forest.end());
                    should_clean = true;
                }
                else{
                    cleaned_forest.push_back(node);
                }
            }
            forest = cleaned_forest;
        }
        if (forest.size() > 0){
            print_forest(forest);
        }
        return forest;
    }

    void get_sub_forest(TreeNode* root, vector<int>& to_delete, vector<TreeNode*>& forest){
        vector<TreeNode*> forest_left, forest_right;
        // Find the sub trees given nodes are being removed
        if (root->left){
            forest_left = delNodes_helper(root->left, to_delete);
        }
        if (root->right){
            forest_right = delNodes_helper(root->right, to_delete);
        }
        forest.insert(forest.end(), forest_left.begin(), forest_left.end());
        forest.insert(forest.end(), forest_right.begin(), forest_right.end());
    }
    vector<TreeNode*> delNodes_helper(TreeNode* root, vector<int>& to_delete) {
        vector<TreeNode*> forest;
        // Current node should be deleted
        for (auto v: to_delete){
            if (root->val == v){
                if (root->left){
                    forest.push_back(root->left);
                }
                if (root->right){
                    forest.push_back(root->right);
                }
                break;
            }
        }
        // Find the sub trees of the current nodes
        get_sub_forest(root, to_delete, forest);
        // Deals with leaves for specific nodes that should be set to null
        for (auto v: to_delete){
            if (root->left and root->left->val == v){
                root->left = NULL;
            }
            if (root->right and root->right->val == v){
                root->right = NULL;
            }
        }
        return forest;
    }
};

int main(int argc, const char * argv[]) {
    TreeNode* root;
    std::vector<int> nums, to_delete;
    Solution sol;
    std::vector<TreeNode*> forest;

    // Tests
    nums = {1,2,3,4,5,-1, -1, -1, -1, 6,7};
    to_delete = {3,5};
    root = get_tree(nums);
    forest = sol.delNodes(root, to_delete);
    cout << "Test 1 Passes" << endl << endl;

    nums = {1,2,4,3,-1,-1,-1,5,-1};
    to_delete = {4, 1};
    root = get_tree(nums);
    forest = sol.delNodes(root, to_delete);
    cout << "Test 2 Passes" << endl << endl;



}