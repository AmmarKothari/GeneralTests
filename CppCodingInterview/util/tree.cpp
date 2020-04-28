#include <cstddef>
#include <iostream>
#include <vector>
#include<fstream>


struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode(int x) : val(x), left(NULL), right(NULL) {}
};


void print_tree_node(TreeNode* node){
    std::printf("Node Value: %d, ", node->val);
    if (node->left and node->right) {
        std::printf("Left: %d, Right: %d\n", node->left->val, node->right->val);
    }
    else if (node->left and !(node->right)){
        std::printf("Left: %d, Right: NULL\n", node->left->val);
    }
    else if (!(node->left) and node->right){
        std::printf("Left: NULL, Right: %d\n", node->right->val);
    }
    else{
        std::printf("Left: NULL, Right: NULL\n");
    }
}

void print_forest(std::vector<TreeNode*> forest){
    std::cout << "Forest: " << std::endl;
    for (auto node: forest){
        print_tree_node(node);
    }
}

template<class T>
void print_vector(std::vector<T> vec){
    for (auto v: vec){
        std::cout << v << ",";
    }
    if (vec.size() > 0){
        std::cout << std::endl;    
    }
}


void build_remaining_tree(TreeNode* root, std::vector<int> &sub_vector){
    if (sub_vector[0] != -1){
        root->left = new TreeNode(sub_vector[0]);
    }
    if (sub_vector[1] != -1){
        root->right = new TreeNode(sub_vector[1]);
    }
    sub_vector.erase(sub_vector.cbegin(), sub_vector.cbegin()+2);
    // print_vector(sub_vector);
    if (sub_vector.size() > 0){
        TreeNode* left = root->left;
        if (root->left and root->left->val){
            build_remaining_tree(root->left, sub_vector);
        }
        TreeNode* right = root->right;
        if (root->right and root->right->val){
            build_remaining_tree(root->right, sub_vector);
        }
    }
    print_tree_node(root);
}

TreeNode* get_tree(std::vector<int> nums){
    print_vector(nums);
    TreeNode* root;
    root = new TreeNode(nums[0]);
    std::vector<int> sub_vector(nums.cbegin()+1, nums.cend());
    print_vector(sub_vector);
    build_remaining_tree(root, sub_vector);
    return root;
}

// int main(){
//     std::vector<int> test = {1, 2, 3, -1, -1, 4, 5};
//     TreeNode* root;
//     root = get_tree(test);
// }