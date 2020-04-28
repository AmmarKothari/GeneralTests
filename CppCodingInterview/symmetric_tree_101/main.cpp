#include <iostream>
#include <assert.h>
#include "tree.cpp"
#include <vector>

bool is_tree_symmetric(TreeNode* root){
    // Collect the values in each layer
    // Check if they are even
    // If they are equal, then proceed to next layer
    std::vector<TreeNode*> layer_nodes;
    std::vector<TreeNode*> next_layer_nodes;
    layer_nodes.push_back(root);
    bool is_tree_symmetric = true;
    bool is_layer_symmetric = true;
    int dist_between_it = 10000000;
    std::vector<TreeNode*>::iterator start, end;
    while (layer_nodes.size() > 0){
        for (auto node: layer_nodes){
            if (node){
                next_layer_nodes.push_back(node->left);
                next_layer_nodes.push_back(node->right);
            }
        }
        if (layer_nodes.size() == 0){
            dist_between_it = 0;
        }
        else{
            start = layer_nodes.begin();
            // Change the end iterator to start at the end of the vector
            end = prev(layer_nodes.end(), 1);
            dist_between_it = std::distance(start, end);
        }
        is_layer_symmetric = true;
        while (dist_between_it > 0){
            // if start is null and end is not null
            if (!(bool)*start or !(bool)*end){
                if ((bool)*start != (bool)*end){
                    is_layer_symmetric = false;
                }
            }
            else if ((*start)->val != (*end)->val) {
                std::printf("Comparison %d to %d\n", (*start)->val, (*end)->val);
                is_layer_symmetric = false;
                break;
            }
            start = next(start);
            end = prev(end);
            dist_between_it = std::distance(start, end);
        }
        if (!is_layer_symmetric){
            is_tree_symmetric = false;
            break;
        }
        layer_nodes = next_layer_nodes;
        next_layer_nodes.clear();
    }
    return (int)is_tree_symmetric;
}

int main(int argc, const char * argv[]) {
    TreeNode* root;
    std::vector<int> nums;
    bool sol;

    // Tests
    nums = {1,2,2,3,4,-1, -1, -1, -1, 4,3};
    root = get_tree(nums);
    sol = is_tree_symmetric(root);
    assert(sol);
    std::cout << "Test 1 passes\n" << std::endl;

    nums = {1,2,2,-1,3,-1,-1,-1,3};
    root = get_tree(nums);
    sol = is_tree_symmetric(root);
    assert(!sol);
    std::cout << "Test 2 passes\n" << std::endl;

}