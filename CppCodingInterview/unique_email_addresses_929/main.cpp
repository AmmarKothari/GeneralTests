#include <vector>
#include <string>
#include <set>
#include <iostream>

using namespace std;

class Solution {
public:
    int numUniqueEmails(vector<string>& emails) {
        set<string> unique_emails;
        string processed_email;
        string user_name;
        string domain;
        bool skip_remaining = false;
        for (auto email: emails){
            cout << email << endl;
            string::iterator it = email.begin();
            skip_remaining = false;
            while (it != email.end()){
                if (*it == '@'){
                    it = next(it);
                    break;
                }
                else if (*it == '+' or skip_remaining){
                    it = next(it);
                    skip_remaining=true;
                }
                else if (*it == '.'){
                    it = next(it);
                }
                else{
                    user_name.push_back(*it);
                    it = next(it);
                }
            }
            for (; it != email.end(); it++){
                domain.push_back(*it);
                // it = next(it);
            }
            processed_email.reserve(user_name.size() + domain.size() + 1);
            processed_email.insert(processed_email.end(), user_name.begin(), user_name.end());
            processed_email.push_back('@');
            processed_email.insert(processed_email.end(), domain.begin(), domain.end());
            for (auto v: processed_email){
                cout << v;
            }
            cout << endl;
            if (unique_emails.count(processed_email) == 0){
                unique_emails.insert(processed_email);
            }
            processed_email.clear();
            user_name.clear();
            domain.clear();
        }
    return (int) unique_emails.size();
    }
};

int main(){
    Solution sol;

    // Tests
    vector<string> emails = {"test.email+alex@leetcode.com","test.e.mail+bob.cathy@leetcode.com","testemail+david@lee.tcode.com"};
    int num = sol.numUniqueEmails(emails);
    assert(num==2);

}