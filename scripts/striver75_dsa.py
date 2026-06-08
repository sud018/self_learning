"""Striver 75 DSA problems with Java starter code."""

STRIVER_75 = [
  # ── ARRAYS (Days 1-10) ──────────────────────────────────────────────────────
  {
    "id": "dsa_two_sum", "category": "DSA", "difficulty": "Easy",
    "title": "Two Sum",
    "statement": "Given an array of integers nums and a target integer, return the indices of the two numbers that add up to target. Each input has exactly one solution. You may not use the same element twice.",
    "examples": ["nums=[2,7,11,15], target=9 -> [0,1]", "nums=[3,2,4], target=6 -> [1,2]"],
    "constraints": ["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "Only one valid answer exists"],
    "testCases": ["[3,3], target=6 -> [0,1]", "[1,2,3,4], target=7 -> [2,3]"],
    "targetMinutes": 20,
    "starterCode": "public int[] twoSum(int[] nums, int target) {\n    // Use a HashMap: store value->index\n    // For each num, check if (target - num) exists in map\n    return new int[]{};\n}"
  },
  {
    "id": "dsa_best_time_stock", "category": "DSA", "difficulty": "Easy",
    "title": "Best Time to Buy and Sell Stock",
    "statement": "Given an array prices where prices[i] is the price of a stock on day i, return the maximum profit you can achieve. You may only buy once and sell once. If no profit is possible, return 0.",
    "examples": ["prices=[7,1,5,3,6,4] -> 5", "prices=[7,6,4,3,1] -> 0"],
    "constraints": ["1 <= prices.length <= 10^5", "0 <= prices[i] <= 10^4"],
    "testCases": ["[1,2] -> 1", "[2,1,2,1] -> 1"],
    "targetMinutes": 15,
    "starterCode": "public int maxProfit(int[] prices) {\n    // Track minPrice seen so far\n    // At each step: profit = price - minPrice, update maxProfit\n    return 0;\n}"
  },
  {
    "id": "dsa_contains_duplicate", "category": "DSA", "difficulty": "Easy",
    "title": "Contains Duplicate",
    "statement": "Given an integer array nums, return true if any value appears at least twice in the array, and false if every element is distinct.",
    "examples": ["[1,2,3,1] -> true", "[1,2,3,4] -> false"],
    "constraints": ["1 <= nums.length <= 10^5", "-10^9 <= nums[i] <= 10^9"],
    "testCases": ["[1,1,1,3,3,4,3,2,4,2] -> true", "[1] -> false"],
    "targetMinutes": 10,
    "starterCode": "public boolean containsDuplicate(int[] nums) {\n    // Use HashSet: add each num, return true if add() returns false\n    return false;\n}"
  },
  {
    "id": "dsa_maximum_subarray", "category": "DSA", "difficulty": "Medium",
    "title": "Maximum Subarray (Kadane's Algorithm)",
    "statement": "Given an integer array nums, find the contiguous subarray which has the largest sum and return its sum. This is the classic Kadane's algorithm problem.",
    "examples": ["[-2,1,-3,4,-1,2,1,-5,4] -> 6  (subarray [4,-1,2,1])", "[1] -> 1", "[5,4,-1,7,8] -> 23"],
    "constraints": ["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"],
    "testCases": ["[-1,-2,-3] -> -1", "[0,-1,0] -> 0"],
    "targetMinutes": 20,
    "starterCode": "public int maxSubArray(int[] nums) {\n    // currentSum = max(nums[i], currentSum + nums[i])\n    // maxSum = max(maxSum, currentSum)\n    return 0;\n}"
  },
  {
    "id": "dsa_product_except_self", "category": "DSA", "difficulty": "Medium",
    "title": "Product of Array Except Self",
    "statement": "Given an integer array nums, return an array answer such that answer[i] equals the product of all elements of nums except nums[i]. Solve it without using division and in O(n) time.",
    "examples": ["[1,2,3,4] -> [24,12,8,6]", "[-1,1,0,-3,3] -> [0,0,9,0,0]"],
    "constraints": ["2 <= nums.length <= 10^5", "-30 <= nums[i] <= 30", "Guaranteed product fits in 32-bit integer"],
    "testCases": ["[2,3] -> [3,2]", "[1,1,1,1] -> [1,1,1,1]"],
    "targetMinutes": 25,
    "starterCode": "public int[] productExceptSelf(int[] nums) {\n    // Pass 1 (left to right): prefix products\n    // Pass 2 (right to left): multiply by suffix products\n    return new int[]{};\n}"
  },
  {
    "id": "dsa_max_product_subarray", "category": "DSA", "difficulty": "Medium",
    "title": "Maximum Product Subarray",
    "statement": "Given an integer array nums, find a contiguous subarray that has the largest product, and return its product. Be careful: negatives can flip max and min.",
    "examples": ["[2,3,-2,4] -> 6", "[-2,0,-1] -> 0"],
    "constraints": ["1 <= nums.length <= 2*10^4", "-10 <= nums[i] <= 10"],
    "testCases": ["[-2] -> -2", "[0,2] -> 2", "[-2,3,-4] -> 24"],
    "targetMinutes": 25,
    "starterCode": "public int maxProduct(int[] nums) {\n    // Track both maxProd and minProd at each position\n    // At negative number, swap max and min\n    return 0;\n}"
  },
  {
    "id": "dsa_find_min_rotated", "category": "DSA", "difficulty": "Medium",
    "title": "Find Minimum in Rotated Sorted Array",
    "statement": "Given a sorted array rotated between 1 and n times, find the minimum element. You must write an O(log n) algorithm.",
    "examples": ["[3,4,5,1,2] -> 1", "[4,5,6,7,0,1,2] -> 0", "[11,13,15,17] -> 11"],
    "constraints": ["n == nums.length", "1 <= n <= 5000", "All values are unique"],
    "testCases": ["[1] -> 1", "[2,1] -> 1", "[5,1,2,3,4] -> 1"],
    "targetMinutes": 20,
    "starterCode": "public int findMin(int[] nums) {\n    // Binary search: if nums[mid] > nums[right], min is in right half\n    // else min is in left half (including mid)\n    return 0;\n}"
  },
  {
    "id": "dsa_search_rotated", "category": "DSA", "difficulty": "Medium",
    "title": "Search in Rotated Sorted Array",
    "statement": "Given a rotated sorted array and a target, return the index of target or -1 if not found. You must write an O(log n) algorithm.",
    "examples": ["nums=[4,5,6,7,0,1,2], target=0 -> 4", "nums=[4,5,6,7,0,1,2], target=3 -> -1"],
    "constraints": ["1 <= nums.length <= 5000", "All values are unique", "-10^4 <= nums[i], target <= 10^4"],
    "testCases": ["[1], target=0 -> -1", "[1], target=1 -> 0"],
    "targetMinutes": 25,
    "starterCode": "public int search(int[] nums, int target) {\n    // Modified binary search: determine which half is sorted\n    // Check if target is in the sorted half, adjust pointers accordingly\n    return -1;\n}"
  },
  {
    "id": "dsa_three_sum", "category": "DSA", "difficulty": "Medium",
    "title": "3Sum",
    "statement": "Given an integer array nums, return all triplets [nums[i], nums[j], nums[k]] such that i != j != k and nums[i] + nums[j] + nums[k] == 0. The solution set must not contain duplicate triplets.",
    "examples": ["[-1,0,1,2,-1,-4] -> [[-1,-1,2],[-1,0,1]]", "[0,1,1] -> []", "[0,0,0] -> [[0,0,0]]"],
    "constraints": ["3 <= nums.length <= 3000", "-10^5 <= nums[i] <= 10^5"],
    "testCases": ["[0,0,0,0] -> [[0,0,0]]", "[-2,0,1,1,2] -> [[-2,0,2],[-2,1,1]]"],
    "targetMinutes": 30,
    "starterCode": "public List<List<Integer>> threeSum(int[] nums) {\n    // Sort array. For each i, use two pointers l=i+1, r=end\n    // Skip duplicates for i, l, r\n    return new ArrayList<>();\n}"
  },
  {
    "id": "dsa_container_water", "category": "DSA", "difficulty": "Medium",
    "title": "Container With Most Water",
    "statement": "Given n non-negative integers representing heights of lines, find two lines that together with the x-axis form a container that holds the most water. Return the maximum amount of water.",
    "examples": ["[1,8,6,2,5,4,8,3,7] -> 49", "[1,1] -> 1"],
    "constraints": ["n == height.length", "2 <= n <= 10^5", "0 <= height[i] <= 10^4"],
    "testCases": ["[4,3,2,1,4] -> 16", "[1,2,1] -> 2"],
    "targetMinutes": 20,
    "starterCode": "public int maxArea(int[] height) {\n    // Two pointers: l=0, r=end\n    // area = min(height[l],height[r]) * (r-l)\n    // Move the pointer with smaller height inward\n    return 0;\n}"
  },

  # ── BINARY SEARCH (Days 11-15) ───────────────────────────────────────────────
  {
    "id": "dsa_binary_search", "category": "DSA", "difficulty": "Easy",
    "title": "Binary Search",
    "statement": "Given a sorted array of n integers and a target value, return the index if target is found. If not, return -1. You must write an algorithm with O(log n) runtime complexity.",
    "examples": ["nums=[-1,0,3,5,9,12], target=9 -> 4", "nums=[-1,0,3,5,9,12], target=2 -> -1"],
    "constraints": ["1 <= nums.length <= 10^4", "All nums are unique and sorted ascending"],
    "testCases": ["[5], target=5 -> 0", "[1,3,5], target=3 -> 1"],
    "targetMinutes": 15,
    "starterCode": "public int search(int[] nums, int target) {\n    int lo = 0, hi = nums.length - 1;\n    while (lo <= hi) {\n        int mid = lo + (hi - lo) / 2;\n        // compare nums[mid] with target\n    }\n    return -1;\n}"
  },
  {
    "id": "dsa_search_2d_matrix", "category": "DSA", "difficulty": "Medium",
    "title": "Search a 2D Matrix",
    "statement": "Write an efficient algorithm that searches for a value in an m x n matrix. Integers in each row are sorted left to right, and the first integer of each row is greater than the last of the previous row.",
    "examples": ["matrix=[[1,3,5,7],[10,11,16,20],[23,30,34,60]], target=3 -> true", "same matrix, target=13 -> false"],
    "constraints": ["m == matrix.length", "n == matrix[i].length", "1 <= m, n <= 100"],
    "testCases": ["[[1]], target=1 -> true", "[[1]], target=2 -> false"],
    "targetMinutes": 20,
    "starterCode": "public boolean searchMatrix(int[][] matrix, int target) {\n    // Treat 2D as 1D: mid = m*n/2\n    // row = mid/n, col = mid%n\n    return false;\n}"
  },
  {
    "id": "dsa_find_peak_element", "category": "DSA", "difficulty": "Medium",
    "title": "Find Peak Element",
    "statement": "A peak element is an element strictly greater than its neighbors. Given an integer array nums, find a peak element and return its index. If multiple peaks exist, return any.",
    "examples": ["[1,2,3,1] -> 2", "[1,2,1,3,5,6,4] -> 1 or 5"],
    "constraints": ["1 <= nums.length <= 1000", "nums[-1] = nums[n] = -infinity"],
    "testCases": ["[1] -> 0", "[1,2] -> 1"],
    "targetMinutes": 20,
    "starterCode": "public int findPeakElement(int[] nums) {\n    // Binary search: if nums[mid] < nums[mid+1], peak is to the right\n    // else peak is at mid or to the left\n    return 0;\n}"
  },
  {
    "id": "dsa_koko_bananas", "category": "DSA", "difficulty": "Medium",
    "title": "Koko Eating Bananas",
    "statement": "Koko has n piles of bananas. In h hours she must eat all bananas. She eats at most k bananas per hour from one pile. Find the minimum integer k such that she can eat all bananas within h hours.",
    "examples": ["piles=[3,6,7,11], h=8 -> 4", "piles=[30,11,23,4,20], h=5 -> 30"],
    "constraints": ["1 <= piles.length <= 10^4", "piles.length <= h <= 10^9", "1 <= piles[i] <= 10^9"],
    "testCases": ["[2,2], h=2 -> 2", "[1,1,1,1], h=4 -> 1"],
    "targetMinutes": 25,
    "starterCode": "public int minEatingSpeed(int[] piles, int h) {\n    // Binary search on k from 1 to max(piles)\n    // For each k, check total hours = sum(ceil(pile/k))\n    return 0;\n}"
  },
  {
    "id": "dsa_median_two_sorted", "category": "DSA", "difficulty": "Hard",
    "title": "Median of Two Sorted Arrays",
    "statement": "Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays. The overall run time complexity must be O(log(m+n)).",
    "examples": ["nums1=[1,3], nums2=[2] -> 2.0", "nums1=[1,2], nums2=[3,4] -> 2.5"],
    "constraints": ["0 <= m, n <= 1000", "1 <= m+n", "-10^6 <= nums1[i], nums2[i] <= 10^6"],
    "testCases": ["[0,0],[0,0] -> 0.0", "[], [1] -> 1.0"],
    "targetMinutes": 40,
    "starterCode": "public double findMedianSortedArrays(int[] nums1, int[] nums2) {\n    // Ensure nums1 is smaller. Binary search partition on nums1\n    // Partition such that left halves combined = right halves combined\n    return 0.0;\n}"
  },

  # ── STRINGS (Days 16-23) ─────────────────────────────────────────────────────
  {
    "id": "dsa_valid_anagram", "category": "DSA", "difficulty": "Easy",
    "title": "Valid Anagram",
    "statement": "Given two strings s and t, return true if t is an anagram of s, and false otherwise. An anagram uses the same characters the same number of times.",
    "examples": ["s=anagram, t=nagaram -> true", "s=rat, t=car -> false"],
    "constraints": ["1 <= s.length, t.length <= 5*10^4", "s and t consist of lowercase English letters"],
    "testCases": ["s=a, t=a -> true", "s=ab, t=ba -> true", "s=aa, t=ab -> false"],
    "targetMinutes": 15,
    "starterCode": "public boolean isAnagram(String s, String t) {\n    // Option 1: sort both strings, compare\n    // Option 2: int[26] freq array for s, subtract for t\n    return false;\n}"
  },
  {
    "id": "dsa_valid_palindrome", "category": "DSA", "difficulty": "Easy",
    "title": "Valid Palindrome",
    "statement": "A phrase is a palindrome if, after converting all uppercase letters to lowercase and removing all non-alphanumeric characters, it reads the same forward and backward. Given a string s, return true if it is a palindrome.",
    "examples": ["s=A man, a plan, a canal: Panama -> true", "s=race a car -> false"],
    "constraints": ["1 <= s.length <= 2*10^5", "s consists only of printable ASCII characters"],
    "testCases": ["s= -> true", "s=a -> true", "s=aba -> true", "s=abc -> false"],
    "targetMinutes": 15,
    "starterCode": "public boolean isPalindrome(String s) {\n    // Two pointers l=0, r=end\n    // Skip non-alphanumeric chars, compare lowercase chars\n    return false;\n}"
  },
  {
    "id": "dsa_longest_substr_no_repeat", "category": "DSA", "difficulty": "Medium",
    "title": "Longest Substring Without Repeating Characters",
    "statement": "Given a string s, find the length of the longest substring without repeating characters.",
    "examples": ["s=abcabcbb -> 3 (abc)", "s=bbbbb -> 1 (b)", "s=pwwkew -> 3 (wke)"],
    "constraints": ["0 <= s.length <= 5*10^4", "s consists of English letters, digits, symbols, spaces"],
    "testCases": ["s='' -> 0", "s=au -> 2", "s=dvdf -> 3"],
    "targetMinutes": 20,
    "starterCode": "public int lengthOfLongestSubstring(String s) {\n    // Sliding window with HashMap<char, lastIndex>\n    // When duplicate found, move left pointer past last occurrence\n    return 0;\n}"
  },
  {
    "id": "dsa_group_anagrams", "category": "DSA", "difficulty": "Medium",
    "title": "Group Anagrams",
    "statement": "Given an array of strings strs, group the anagrams together. You can return the answer in any order.",
    "examples": ["[eat,tea,tan,ate,nat,bat] -> [[bat],[nat,tan],[ate,eat,tea]]"],
    "constraints": ["1 <= strs.length <= 10^4", "0 <= strs[i].length <= 100", "strs[i] consists of lowercase letters"],
    "testCases": ["[\"\"] -> [[\"\"]]", "[\"a\"] -> [[\"a\"]]"],
    "targetMinutes": 20,
    "starterCode": "public List<List<String>> groupAnagrams(String[] strs) {\n    // Key = sorted string (or freq count array as string)\n    // HashMap<String, List<String>> groups\n    return new ArrayList<>();\n}"
  },
  {
    "id": "dsa_min_window_substr", "category": "DSA", "difficulty": "Hard",
    "title": "Minimum Window Substring",
    "statement": "Given strings s and t, return the minimum window substring of s such that every character in t (including duplicates) is included in the window. If no valid window exists, return empty string.",
    "examples": ["s=ADOBECODEBANC, t=ABC -> BANC", "s=a, t=a -> a", "s=a, t=aa -> ''"],
    "constraints": ["1 <= s.length, t.length <= 10^5"],
    "testCases": ["s=aa, t=aa -> aa", "s=ab, t=b -> b"],
    "targetMinutes": 40,
    "starterCode": "public String minWindow(String s, String t) {\n    // Sliding window: expand right until all t chars found\n    // Then contract left to minimize window\n    // Track with need[] and window[] frequency arrays\n    return \"\";\n}"
  },
  {
    "id": "dsa_longest_repeating_replacement", "category": "DSA", "difficulty": "Medium",
    "title": "Longest Repeating Character Replacement",
    "statement": "Given a string s and an integer k, you can choose any character and change it to any other uppercase letter at most k times. Return the length of the longest substring containing the same letter after the operations.",
    "examples": ["s=ABAB, k=2 -> 4", "s=AABABBA, k=1 -> 4"],
    "constraints": ["1 <= s.length <= 10^5", "s consists of only uppercase letters", "0 <= k <= s.length"],
    "testCases": ["s=A, k=0 -> 1", "s=AAAA, k=2 -> 4"],
    "targetMinutes": 30,
    "starterCode": "public int characterReplacement(String s, int k) {\n    // Sliding window: window is valid if windowLen - maxFreq <= k\n    // Track freq of each char in window with int[26]\n    return 0;\n}"
  },
  {
    "id": "dsa_palindromic_substrings", "category": "DSA", "difficulty": "Medium",
    "title": "Palindromic Substrings",
    "statement": "Given a string s, return the number of palindromic substrings in it. A string is a palindrome when it reads the same backward as forward. A substring is a contiguous sequence of characters.",
    "examples": ["s=abc -> 3 (a,b,c)", "s=aaa -> 6 (a,a,a,aa,aa,aaa)"],
    "constraints": ["1 <= s.length <= 1000", "s consists of lowercase English letters"],
    "testCases": ["s=a -> 1", "s=ab -> 2", "s=aba -> 4"],
    "targetMinutes": 25,
    "starterCode": "public int countSubstrings(String s) {\n    // Expand around center for each position (odd & even length)\n    // Count each valid palindrome expansion\n    return 0;\n}"
  },
  {
    "id": "dsa_longest_palindrome_substr", "category": "DSA", "difficulty": "Medium",
    "title": "Longest Palindromic Substring",
    "statement": "Given a string s, return the longest palindromic substring in s.",
    "examples": ["s=babad -> bab (or aba)", "s=cbbd -> bb"],
    "constraints": ["1 <= s.length <= 1000", "s consists of only digits and English letters"],
    "testCases": ["s=a -> a", "s=ac -> a", "s=racecar -> racecar"],
    "targetMinutes": 25,
    "starterCode": "public String longestPalindrome(String s) {\n    // Expand around center: try every index as center\n    // Handle both odd-length (i,i) and even-length (i,i+1) centers\n    return \"\";\n}"
  },

  # ── LINKED LIST (Days 24-29) ─────────────────────────────────────────────────
  {
    "id": "dsa_reverse_linked_list", "category": "DSA", "difficulty": "Easy",
    "title": "Reverse Linked List",
    "statement": "Given the head of a singly linked list, reverse the list and return the reversed list.",
    "examples": ["1->2->3->4->5 -> 5->4->3->2->1", "1->2 -> 2->1", "[] -> []"],
    "constraints": ["0 <= number of nodes <= 5000", "-5000 <= Node.val <= 5000"],
    "testCases": ["[1] -> [1]", "[1,2] -> [2,1]"],
    "targetMinutes": 15,
    "starterCode": "// class ListNode { int val; ListNode next; ListNode(int v){val=v;} }\npublic ListNode reverseList(ListNode head) {\n    // Iterative: prev=null, curr=head\n    // while curr != null: store next, curr.next=prev, prev=curr, curr=next\n    return null;\n}"
  },
  {
    "id": "dsa_merge_two_sorted_lists", "category": "DSA", "difficulty": "Easy",
    "title": "Merge Two Sorted Lists",
    "statement": "You are given the heads of two sorted linked lists list1 and list2. Merge the two lists into one sorted list and return its head.",
    "examples": ["1->2->4, 1->3->4 -> 1->1->2->3->4->4", "[], [] -> []"],
    "constraints": ["0 <= number of nodes in each list <= 50", "-100 <= Node.val <= 100"],
    "testCases": ["[1,3],[2] -> [1,2,3]", "[],[1] -> [1]"],
    "targetMinutes": 20,
    "starterCode": "public ListNode mergeTwoLists(ListNode l1, ListNode l2) {\n    // Use dummy head node\n    // Compare l1.val and l2.val, attach smaller, advance that pointer\n    return null;\n}"
  },
  {
    "id": "dsa_linked_list_cycle", "category": "DSA", "difficulty": "Easy",
    "title": "Linked List Cycle Detection",
    "statement": "Given the head of a linked list, determine if the list has a cycle. A cycle occurs if some node can be reached again by continuously following next pointers.",
    "examples": ["3->2->0->-4->back to 2 -> true", "1->2->back to 1 -> true", "1 -> false"],
    "constraints": ["0 <= number of nodes <= 10^4", "-10^5 <= Node.val <= 10^5"],
    "testCases": ["No cycle -> false", "One node pointing to itself -> true"],
    "targetMinutes": 15,
    "starterCode": "public boolean hasCycle(ListNode head) {\n    // Floyd's algorithm: slow moves 1 step, fast moves 2 steps\n    // If they meet, cycle exists\n    return false;\n}"
  },
  {
    "id": "dsa_remove_nth_node", "category": "DSA", "difficulty": "Medium",
    "title": "Remove Nth Node From End of List",
    "statement": "Given the head of a linked list, remove the nth node from the end of the list and return its head. Do it in one pass.",
    "examples": ["1->2->3->4->5, n=2 -> 1->2->3->5", "1, n=1 -> []", "1->2, n=1 -> [1]"],
    "constraints": ["1 <= number of nodes <= 30", "0 <= Node.val <= 100", "1 <= n <= size"],
    "testCases": ["[1,2], n=2 -> [2]", "[1], n=1 -> []"],
    "targetMinutes": 20,
    "starterCode": "public ListNode removeNthFromEnd(ListNode head, int n) {\n    // Two pointers: advance fast n steps ahead\n    // Then move both until fast reaches end\n    // slow.next is the node to remove\n    return null;\n}"
  },
  {
    "id": "dsa_reorder_list", "category": "DSA", "difficulty": "Medium",
    "title": "Reorder List",
    "statement": "Given the head of a singly linked list: L0->L1->...->Ln-1->Ln, reorder it to: L0->Ln->L1->Ln-1->L2->Ln-2->... Do this in-place without altering nodes' values.",
    "examples": ["1->2->3->4 -> 1->4->2->3", "1->2->3->4->5 -> 1->5->2->4->3"],
    "constraints": ["1 <= number of nodes <= 5*10^4", "1 <= Node.val <= 1000"],
    "testCases": ["[1] -> [1]", "[1,2] -> [1,2]"],
    "targetMinutes": 30,
    "starterCode": "public void reorderList(ListNode head) {\n    // Step 1: find middle (slow/fast pointers)\n    // Step 2: reverse second half\n    // Step 3: merge first half and reversed second half\n}"
  },
  {
    "id": "dsa_merge_k_sorted_lists", "category": "DSA", "difficulty": "Hard",
    "title": "Merge K Sorted Lists",
    "statement": "You are given an array of k linked-lists, each sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.",
    "examples": ["[[1,4,5],[1,3,4],[2,6]] -> 1->1->2->3->4->4->5->6", "[] -> []"],
    "constraints": ["k == lists.length", "0 <= k <= 10^4", "0 <= lists[i].length <= 500"],
    "testCases": ["[[]] -> []", "[[1],[0]] -> [0,1]"],
    "targetMinutes": 35,
    "starterCode": "public ListNode mergeKLists(ListNode[] lists) {\n    // Use a Min-Heap (PriorityQueue) of size k\n    // Poll minimum node, add to result, push its next into heap\n    return null;\n}"
  },

  # ── STACK (Days 30-36) ───────────────────────────────────────────────────────
  {
    "id": "dsa_valid_parentheses", "category": "DSA", "difficulty": "Easy",
    "title": "Valid Parentheses",
    "statement": "Given a string s containing just '(', ')', '{', '}', '[' and ']', determine if the input string is valid. Open brackets must be closed by the same type and in correct order.",
    "examples": ["() -> true", "()[]{} -> true", "(] -> false", "([)] -> false", "{[]} -> true"],
    "constraints": ["1 <= s.length <= 10^4", "s consists of parentheses only"],
    "testCases": ["( -> false", ") -> false", "({}) -> true"],
    "targetMinutes": 15,
    "starterCode": "public boolean isValid(String s) {\n    // Stack: push open brackets\n    // For close bracket: if stack empty or top doesn't match, return false\n    return false;\n}"
  },
  {
    "id": "dsa_min_stack", "category": "DSA", "difficulty": "Medium",
    "title": "Min Stack",
    "statement": "Design a stack that supports push, pop, top, and retrieving the minimum element in constant time. Implement MinStack with push(val), pop(), top(), and getMin() methods.",
    "examples": ["push(-2),push(0),push(-3),getMin()->-3,pop(),top()->0,getMin()->-2"],
    "constraints": ["-2^31 <= val <= 2^31-1", "pop/top/getMin called on non-empty stack", "At most 3*10^4 operations"],
    "testCases": ["push(1),push(2),getMin()->1", "push(0),push(1),push(0),getMin()->0,pop(),getMin()->0"],
    "targetMinutes": 20,
    "starterCode": "class MinStack {\n    // Use two stacks: one regular, one to track minimums\n    // Or store (value, currentMin) pairs in one stack\n    public void push(int val) { }\n    public void pop() { }\n    public int top() { return 0; }\n    public int getMin() { return 0; }\n}"
  },
  {
    "id": "dsa_daily_temperatures", "category": "DSA", "difficulty": "Medium",
    "title": "Daily Temperatures",
    "statement": "Given an array temperatures, return an array answer such that answer[i] is the number of days you have to wait after day i to get a warmer temperature. If there is no future day with warmer temperature, answer[i] = 0.",
    "examples": ["[73,74,75,71,69,72,76,73] -> [1,1,4,2,1,1,0,0]", "[30,40,50,60] -> [1,1,1,0]"],
    "constraints": ["1 <= temperatures.length <= 10^5", "30 <= temperatures[i] <= 100"],
    "testCases": ["[30,60,90] -> [1,1,0]", "[89,62,70,58,47,47,46,76,100,70] -> [8,1,5,4,3,2,1,1,0,0]"],
    "targetMinutes": 20,
    "starterCode": "public int[] dailyTemperatures(int[] temperatures) {\n    // Monotonic decreasing stack storing indices\n    // When we find a warmer day, pop and set answer[idx] = i - idx\n    return new int[]{};\n}"
  },
  {
    "id": "dsa_evaluate_rpn", "category": "DSA", "difficulty": "Medium",
    "title": "Evaluate Reverse Polish Notation",
    "statement": "Evaluate the value of an arithmetic expression in Reverse Polish Notation. Valid operators are +, -, *, /. Each operand may be an integer or another expression.",
    "examples": ["[2,1,+,3,*] -> 9", "[4,13,5,/,+] -> 6", "[10,6,9,3,+,-11,*,/,*,17,+,5,+] -> 22"],
    "constraints": ["1 <= tokens.length <= 10^4", "Division truncates toward zero"],
    "testCases": ["[3,4,+] -> 7", "[5,1,2,+,4,*,+,3,-] -> 14"],
    "targetMinutes": 20,
    "starterCode": "public int evalRPN(String[] tokens) {\n    // Stack of integers\n    // When operator found: pop two values, apply op, push result\n    return 0;\n}"
  },
  {
    "id": "dsa_generate_parentheses", "category": "DSA", "difficulty": "Medium",
    "title": "Generate Parentheses",
    "statement": "Given n pairs of parentheses, write a function to generate all combinations of well-formed parentheses.",
    "examples": ["n=3 -> [((())) ,(()()),(())(),()(()),()()()] ", "n=1 -> [()]"],
    "constraints": ["1 <= n <= 8"],
    "testCases": ["n=1 -> [()]", "n=2 -> [(()), ()()]"],
    "targetMinutes": 25,
    "starterCode": "public List<String> generateParenthesis(int n) {\n    // Backtracking: track open count and close count\n    // Add '(' if open < n, add ')' if close < open\n    return new ArrayList<>();\n}"
  },
  {
    "id": "dsa_car_fleet", "category": "DSA", "difficulty": "Medium",
    "title": "Car Fleet",
    "statement": "N cars go to the same destination. Given their positions and speeds, find the number of car fleets that arrive at the destination. A fleet forms when a faster car catches up to a slower car.",
    "examples": ["target=12, position=[10,8,0,5,3], speed=[2,4,1,1,3] -> 3"],
    "constraints": ["n == position.length == speed.length", "1 <= n <= 10^5", "0 < target <= 10^6"],
    "testCases": ["target=10, position=[3], speed=[3] -> 1", "target=100, position=[0,2,4], speed=[4,2,1] -> 1"],
    "targetMinutes": 25,
    "starterCode": "public int carFleet(int target, int[] position, int[] speed) {\n    // Sort by position descending\n    // Compute time to reach target for each car\n    // Use stack: if current time <= stack top, they fleet (pop)\n    return 0;\n}"
  },
  {
    "id": "dsa_largest_rectangle_histogram", "category": "DSA", "difficulty": "Hard",
    "title": "Largest Rectangle in Histogram",
    "statement": "Given an array of integers heights representing the histogram's bar height, return the area of the largest rectangle in the histogram.",
    "examples": ["[2,1,5,6,2,3] -> 10", "[2,4] -> 4"],
    "constraints": ["1 <= heights.length <= 10^5", "0 <= heights[i] <= 10^4"],
    "testCases": ["[1] -> 1", "[1,1] -> 2", "[2,1,2] -> 3"],
    "targetMinutes": 40,
    "starterCode": "public int largestRectangleArea(int[] heights) {\n    // Monotonic increasing stack storing indices\n    // When shorter bar found, pop and calculate area\n    // width = i - stack.peek() - 1\n    return 0;\n}"
  },

  # ── HEAP (Days 37-41) ────────────────────────────────────────────────────────
  {
    "id": "dsa_kth_largest", "category": "DSA", "difficulty": "Medium",
    "title": "Kth Largest Element in an Array",
    "statement": "Given an integer array nums and an integer k, return the kth largest element in the array. Note that it is the kth largest in sorted order, not the kth distinct element.",
    "examples": ["[3,2,1,5,6,4], k=2 -> 5", "[3,2,3,1,2,4,5,5,6], k=4 -> 4"],
    "constraints": ["1 <= k <= nums.length <= 10^4", "-10^4 <= nums[i] <= 10^4"],
    "testCases": ["[1], k=1 -> 1", "[2,1], k=2 -> 1"],
    "targetMinutes": 20,
    "starterCode": "public int findKthLargest(int[] nums, int k) {\n    // Min-Heap of size k\n    // Keep only k largest elements: if heap.size() > k, poll()\n    // Return heap.peek()\n    return 0;\n}"
  },
  {
    "id": "dsa_top_k_frequent", "category": "DSA", "difficulty": "Medium",
    "title": "Top K Frequent Elements",
    "statement": "Given an integer array nums and an integer k, return the k most frequent elements. You may return the answer in any order.",
    "examples": ["[1,1,1,2,2,3], k=2 -> [1,2]", "[1], k=1 -> [1]"],
    "constraints": ["1 <= nums.length <= 10^5", "k is in range [1, number of unique elements]"],
    "testCases": ["[4,1,-1,2,-1,2,3], k=2 -> [-1,2]"],
    "targetMinutes": 20,
    "starterCode": "public int[] topKFrequent(int[] nums, int k) {\n    // Count frequencies with HashMap\n    // Use Min-Heap of size k on frequency\n    // Or bucket sort: bucket[freq] = list of nums\n    return new int[]{};\n}"
  },
  {
    "id": "dsa_k_closest_points", "category": "DSA", "difficulty": "Medium",
    "title": "K Closest Points to Origin",
    "statement": "Given an array of points, return the k closest points to the origin (0,0). The distance is the Euclidean distance. You may return the answer in any order.",
    "examples": ["points=[[1,3],[-2,2]], k=1 -> [[-2,2]]", "points=[[3,3],[5,-1],[-2,4]], k=2 -> [[3,3],[-2,4]]"],
    "constraints": ["1 <= k <= points.length <= 10^4", "-10^4 <= xi, yi <= 10^4"],
    "testCases": ["[[1,0],[0,1]], k=1 -> [[1,0]] or [[0,1]]"],
    "targetMinutes": 20,
    "starterCode": "public int[][] kClosest(int[][] points, int k) {\n    // Max-Heap of size k based on distance squared (x*x + y*y)\n    // When heap.size() > k, poll the farthest\n    return new int[][]{};\n}"
  },
  {
    "id": "dsa_task_scheduler", "category": "DSA", "difficulty": "Medium",
    "title": "Task Scheduler",
    "statement": "Given a char array tasks of CPU tasks and a non-negative integer n (cooldown period), return the minimum number of intervals needed to finish all tasks. Same task must be n intervals apart.",
    "examples": ["tasks=[A,A,A,B,B,B], n=2 -> 8", "tasks=[A,A,A,B,B,B], n=0 -> 6", "tasks=[A,A,A,A,A,A,B,C,D,E,F,G], n=2 -> 16"],
    "constraints": ["1 <= tasks.length <= 10^4", "tasks[i] is uppercase English letter", "0 <= n <= 100"],
    "testCases": ["[A,B,C], n=2 -> 3", "[A,A,A], n=2 -> 7"],
    "targetMinutes": 30,
    "starterCode": "public int leastInterval(char[] tasks, int n) {\n    // Count frequencies. maxFreq = highest frequency\n    // maxCount = number of tasks with maxFreq\n    // result = max(tasks.length, (maxFreq-1)*(n+1) + maxCount)\n    return 0;\n}"
  },
  {
    "id": "dsa_find_median_stream", "category": "DSA", "difficulty": "Hard",
    "title": "Find Median from Data Stream",
    "statement": "Design a data structure that supports: addNum(int num) - adds a number to the data structure, and findMedian() - returns the median of all elements so far. Implement the MedianFinder class.",
    "examples": ["addNum(1), addNum(2), findMedian()->1.5, addNum(3), findMedian()->2.0"],
    "constraints": ["-10^5 <= num <= 10^5", "At least one element before calling findMedian", "At most 5*10^4 calls to addNum and findMedian"],
    "testCases": ["add(1), median()->1.0", "add(1),add(2), median()->1.5"],
    "targetMinutes": 35,
    "starterCode": "class MedianFinder {\n    // Two heaps: maxHeap (left half), minHeap (right half)\n    // Balance: maxHeap.size() == minHeap.size() or +1\n    public void addNum(int num) { }\n    public double findMedian() { return 0.0; }\n}"
  },

  # ── TREES (Days 42-56) ───────────────────────────────────────────────────────
  {
    "id": "dsa_invert_binary_tree", "category": "DSA", "difficulty": "Easy",
    "title": "Invert Binary Tree",
    "statement": "Given the root of a binary tree, invert the tree (mirror it), and return its root.",
    "examples": ["[4,2,7,1,3,6,9] -> [4,7,2,9,6,3,1]", "[2,1,3] -> [2,3,1]", "[] -> []"],
    "constraints": ["0 <= number of nodes <= 100", "-100 <= Node.val <= 100"],
    "testCases": ["single node [1] -> [1]", "[1,2] -> [1,null,2]"],
    "targetMinutes": 15,
    "starterCode": "// class TreeNode { int val; TreeNode left, right; TreeNode(int v){val=v;} }\npublic TreeNode invertTree(TreeNode root) {\n    // Base case: null or leaf\n    // Swap left and right, recurse on both sides\n    return null;\n}"
  },
  {
    "id": "dsa_max_depth_tree", "category": "DSA", "difficulty": "Easy",
    "title": "Maximum Depth of Binary Tree",
    "statement": "Given the root of a binary tree, return its maximum depth. The maximum depth is the number of nodes along the longest path from root to the farthest leaf node.",
    "examples": ["[3,9,20,null,null,15,7] -> 3", "[1,null,2] -> 2"],
    "constraints": ["0 <= number of nodes <= 10^4", "-100 <= Node.val <= 100"],
    "testCases": ["null -> 0", "[1] -> 1"],
    "targetMinutes": 10,
    "starterCode": "public int maxDepth(TreeNode root) {\n    // if root == null return 0\n    // return 1 + max(maxDepth(left), maxDepth(right))\n    return 0;\n}"
  },
  {
    "id": "dsa_same_tree", "category": "DSA", "difficulty": "Easy",
    "title": "Same Tree",
    "statement": "Given the roots of two binary trees p and q, write a function to check if they are the same or not. Two binary trees are identical if structurally identical with the same node values.",
    "examples": ["p=[1,2,3], q=[1,2,3] -> true", "p=[1,2], q=[1,null,2] -> false", "p=[1,2,1], q=[1,1,2] -> false"],
    "constraints": ["0 <= number of nodes <= 100", "-10^4 <= Node.val <= 10^4"],
    "testCases": ["both null -> true", "one null -> false"],
    "targetMinutes": 10,
    "starterCode": "public boolean isSameTree(TreeNode p, TreeNode q) {\n    // Both null -> true\n    // One null -> false\n    // p.val != q.val -> false\n    // return isSameTree(p.left,q.left) && isSameTree(p.right,q.right)\n    return false;\n}"
  },
  {
    "id": "dsa_subtree_another_tree", "category": "DSA", "difficulty": "Easy",
    "title": "Subtree of Another Tree",
    "statement": "Given the roots of two binary trees root and subRoot, return true if there is a subtree of root with the same structure and node values as subRoot, and false otherwise.",
    "examples": ["root=[3,4,5,1,2], subRoot=[4,1,2] -> true", "root=[3,4,5,1,2,null,null,null,null,0], subRoot=[4,1,2] -> false"],
    "constraints": ["1 <= root.length <= 2000", "1 <= subRoot.length <= 1000"],
    "testCases": ["identical trees -> true", "subRoot is a leaf not in root -> false"],
    "targetMinutes": 20,
    "starterCode": "public boolean isSubtree(TreeNode root, TreeNode subRoot) {\n    // At each node, check if isSameTree(root, subRoot)\n    // Recursively check left and right subtrees\n    return false;\n}"
  },
  {
    "id": "dsa_balanced_binary_tree", "category": "DSA", "difficulty": "Easy",
    "title": "Balanced Binary Tree",
    "statement": "Given a binary tree, determine if it is height-balanced. A height-balanced binary tree is one where the left and right subtrees of every node differ in height by no more than 1.",
    "examples": ["[3,9,20,null,null,15,7] -> true", "[1,2,2,3,3,null,null,4,4] -> false", "[] -> true"],
    "constraints": ["0 <= number of nodes <= 5000", "-10^4 <= Node.val <= 10^4"],
    "testCases": ["[1] -> true", "[1,2,null,3] -> false"],
    "targetMinutes": 20,
    "starterCode": "public boolean isBalanced(TreeNode root) {\n    // Helper returns height or -1 if unbalanced\n    // height(null)=0, height(node)=1+max(h(left),h(right))\n    // Return -1 if |h(left)-h(right)| > 1\n    return false;\n}"
  },
  {
    "id": "dsa_diameter_binary_tree", "category": "DSA", "difficulty": "Easy",
    "title": "Diameter of Binary Tree",
    "statement": "Given the root of a binary tree, return the length of the diameter. The diameter is the length of the longest path between any two nodes. This path may or may not pass through the root.",
    "examples": ["[1,2,3,4,5] -> 3 (path: 4->2->1->3 or 5->2->1->3)", "[1,2] -> 1"],
    "constraints": ["1 <= number of nodes <= 10^4", "-100 <= Node.val <= 100"],
    "testCases": ["[1] -> 0", "[1,2,3] -> 2"],
    "targetMinutes": 20,
    "starterCode": "public int diameterOfBinaryTree(TreeNode root) {\n    // For each node: diameter through it = depth(left) + depth(right)\n    // Track global max. DFS helper returns depth.\n    return 0;\n}"
  },
  {
    "id": "dsa_lca_bst", "category": "DSA", "difficulty": "Medium",
    "title": "Lowest Common Ancestor of BST",
    "statement": "Given a BST, find the lowest common ancestor (LCA) of two given nodes p and q. The LCA is defined as the lowest node that has both p and q as descendants (a node can be a descendant of itself).",
    "examples": ["root=[6,2,8,0,4,7,9], p=2, q=8 -> 6", "root=[6,2,8,0,4,7,9], p=2, q=4 -> 2"],
    "constraints": ["2 <= number of nodes <= 10^5", "All values are unique", "p and q exist in the tree"],
    "testCases": ["p=root, q=any -> root", "p and q same side -> that side's ancestor"],
    "targetMinutes": 15,
    "starterCode": "public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {\n    // If both p and q are less than root, go left\n    // If both greater, go right\n    // Else root is the LCA\n    return null;\n}"
  },
  {
    "id": "dsa_level_order_traversal", "category": "DSA", "difficulty": "Medium",
    "title": "Binary Tree Level Order Traversal",
    "statement": "Given the root of a binary tree, return the level order traversal of its nodes' values (i.e., from left to right, level by level).",
    "examples": ["[3,9,20,null,null,15,7] -> [[3],[9,20],[15,7]]", "[1] -> [[1]]", "[] -> []"],
    "constraints": ["0 <= number of nodes <= 2000", "-1000 <= Node.val <= 1000"],
    "testCases": ["[1,2,3] -> [[1],[2,3]]", "[1,null,2] -> [[1],[2]]"],
    "targetMinutes": 20,
    "starterCode": "public List<List<Integer>> levelOrder(TreeNode root) {\n    // BFS with a Queue\n    // For each level: poll all current level nodes, add their children\n    return new ArrayList<>();\n}"
  },
  {
    "id": "dsa_right_side_view", "category": "DSA", "difficulty": "Medium",
    "title": "Binary Tree Right Side View",
    "statement": "Given the root of a binary tree, imagine yourself standing on the right side of it, return the values of the nodes you can see ordered from top to bottom.",
    "examples": ["[1,2,3,null,5,null,4] -> [1,3,4]", "[1,null,3] -> [1,3]", "[] -> []"],
    "constraints": ["0 <= number of nodes <= 100", "-100 <= Node.val <= 100"],
    "testCases": ["[1] -> [1]", "[1,2] -> [1,2]"],
    "targetMinutes": 20,
    "starterCode": "public List<Integer> rightSideView(TreeNode root) {\n    // BFS level order: take the last node of each level\n    // Or DFS: visit right subtree first, add node if depth > result.size()\n    return new ArrayList<>();\n}"
  },
  {
    "id": "dsa_count_good_nodes", "category": "DSA", "difficulty": "Medium",
    "title": "Count Good Nodes in Binary Tree",
    "statement": "Given a binary tree root, a node X in the tree is named good if in the path from root to X there are no nodes with a value greater than X. Return the number of good nodes.",
    "examples": ["[3,1,4,3,null,1,5] -> 4", "[3,3,null,4,2] -> 3", "[1] -> 1"],
    "constraints": ["1 <= number of nodes <= 10^5", "-10^4 <= Node.val <= 10^4"],
    "testCases": ["[1] -> 1", "[3,1,4,3,null,1,5] -> 4"],
    "targetMinutes": 20,
    "starterCode": "public int goodNodes(TreeNode root) {\n    // DFS with maxSoFar parameter\n    // Node is good if node.val >= maxSoFar\n    // Update maxSoFar = max(maxSoFar, node.val)\n    return 0;\n}"
  },
  {
    "id": "dsa_validate_bst", "category": "DSA", "difficulty": "Medium",
    "title": "Validate Binary Search Tree",
    "statement": "Given the root of a binary tree, determine if it is a valid binary search tree (BST). A valid BST: left subtree nodes are less than node, right subtree nodes are greater, both subtrees are valid BSTs.",
    "examples": ["[2,1,3] -> true", "[5,1,4,null,null,3,6] -> false"],
    "constraints": ["1 <= number of nodes <= 10^4", "-2^31 <= Node.val <= 2^31-1"],
    "testCases": ["[1] -> true", "[2,2,2] -> false"],
    "targetMinutes": 20,
    "starterCode": "public boolean isValidBST(TreeNode root) {\n    // Pass min and max bounds to each node\n    // validate(node, Long.MIN_VALUE, Long.MAX_VALUE)\n    // Left child: max bound = node.val\n    // Right child: min bound = node.val\n    return false;\n}"
  },
  {
    "id": "dsa_kth_smallest_bst", "category": "DSA", "difficulty": "Medium",
    "title": "Kth Smallest Element in BST",
    "statement": "Given the root of a BST and an integer k, return the kth smallest value (1-indexed) of all the values of the nodes in the tree.",
    "examples": ["[3,1,4,null,2], k=1 -> 1", "[5,3,6,2,4,null,null,1], k=3 -> 3"],
    "constraints": ["1 <= k <= n <= 10^4", "0 <= Node.val <= 10^4"],
    "testCases": ["[1], k=1 -> 1", "[2,1,3], k=2 -> 2"],
    "targetMinutes": 20,
    "starterCode": "public int kthSmallest(TreeNode root, int k) {\n    // Inorder traversal of BST gives sorted order\n    // Count nodes during traversal, return kth\n    return 0;\n}"
  },
  {
    "id": "dsa_construct_bt_preorder_inorder", "category": "DSA", "difficulty": "Medium",
    "title": "Construct Binary Tree from Preorder and Inorder Traversal",
    "statement": "Given two integer arrays preorder and inorder, construct and return the binary tree. Preorder = [root, left subtree, right subtree]. Inorder = [left subtree, root, right subtree].",
    "examples": ["preorder=[3,9,20,15,7], inorder=[9,3,15,20,7] -> [3,9,20,null,null,15,7]"],
    "constraints": ["1 <= preorder.length <= 3000", "inorder.length == preorder.length", "All values are unique"],
    "testCases": ["preorder=[1], inorder=[1] -> [1]"],
    "targetMinutes": 30,
    "starterCode": "public TreeNode buildTree(int[] preorder, int[] inorder) {\n    // Root = preorder[0]. Find root index in inorder.\n    // Left size = rootIdxInInorder. Recursively build left and right.\n    // Use HashMap for O(1) inorder lookups\n    return null;\n}"
  },
  {
    "id": "dsa_max_path_sum", "category": "DSA", "difficulty": "Hard",
    "title": "Binary Tree Maximum Path Sum",
    "statement": "A path in a binary tree is a sequence of nodes where each pair of adjacent nodes has an edge. A node can only appear in a path at most once. Given the root, return the maximum path sum.",
    "examples": ["[1,2,3] -> 6", "[-10,9,20,null,null,15,7] -> 42"],
    "constraints": ["1 <= number of nodes <= 3*10^4", "-1000 <= Node.val <= 1000"],
    "testCases": ["[-3] -> -3", "[2,-1] -> 2"],
    "targetMinutes": 35,
    "starterCode": "public int maxPathSum(TreeNode root) {\n    // DFS: for each node compute max gain (only counting one side)\n    // At each node: path through it = left gain + right gain + node.val\n    // Track global max. Return max(node.val, node.val + max(left,right))\n    return 0;\n}"
  },
  {
    "id": "dsa_serialize_deserialize", "category": "DSA", "difficulty": "Hard",
    "title": "Serialize and Deserialize Binary Tree",
    "statement": "Design an algorithm to serialize a binary tree to a string and deserialize the string back to a binary tree. There is no restriction on how you do it; just ensure encode/decode works correctly.",
    "examples": ["root=[1,2,3,null,null,4,5] -> serialize -> deserialize -> same tree"],
    "constraints": ["0 <= number of nodes <= 10^4", "-1000 <= Node.val <= 1000"],
    "testCases": ["null tree -> null", "single node -> same"],
    "targetMinutes": 40,
    "starterCode": "public String serialize(TreeNode root) {\n    // BFS or preorder DFS, use 'N' for null, comma separator\n    return \"\";\n}\npublic TreeNode deserialize(String data) {\n    // Split by comma, reconstruct using queue (BFS) or recursion (DFS)\n    return null;\n}"
  },

  # ── GRAPHS (Days 57-66) ──────────────────────────────────────────────────────
  {
    "id": "dsa_number_of_islands", "category": "DSA", "difficulty": "Medium",
    "title": "Number of Islands",
    "statement": "Given an m x n 2D binary grid representing a map of '1's (land) and '0's (water), return the number of islands. An island is surrounded by water and formed by connecting adjacent '1's horizontally or vertically.",
    "examples": ["[[1,1,1,1,0],[1,1,0,1,0],[1,1,0,0,0],[0,0,0,0,0]] -> 1", "[[1,1,0,0,0],[1,1,0,0,0],[0,0,1,0,0],[0,0,0,1,1]] -> 3"],
    "constraints": ["1 <= m, n <= 300", "grid[i][j] is '0' or '1'"],
    "testCases": ["[[1]] -> 1", "[[1,0],[0,1]] -> 2"],
    "targetMinutes": 25,
    "starterCode": "public int numIslands(char[][] grid) {\n    // For each '1': increment count, then BFS/DFS to mark all connected '1's as visited\n    return 0;\n}"
  },
  {
    "id": "dsa_clone_graph", "category": "DSA", "difficulty": "Medium",
    "title": "Clone Graph",
    "statement": "Given a reference of a node in a connected undirected graph, return a deep copy (clone) of the graph. Each node contains a value (int) and a list of its neighbors.",
    "examples": ["adjList=[[2,4],[1,3],[2,4],[1,3]] -> deep copy of same structure"],
    "constraints": ["1 <= number of nodes <= 100", "1 <= Node.val <= 100", "No repeated edges, no self-loops"],
    "testCases": ["single node with no neighbors -> single clone", "null -> null"],
    "targetMinutes": 25,
    "starterCode": "public Node cloneGraph(Node node) {\n    // HashMap<original node, cloned node>\n    // DFS/BFS: for each neighbor, if not cloned yet, create clone and recurse\n    return null;\n}"
  },
  {
    "id": "dsa_max_area_island", "category": "DSA", "difficulty": "Medium",
    "title": "Max Area of Island",
    "statement": "Given a binary matrix grid, return the maximum area of an island. An island is a group of 1s connected 4-directionally. If no island exists, return 0.",
    "examples": ["various grid -> max connected region size", "all zeros -> 0"],
    "constraints": ["m == grid.length", "n == grid[i].length", "1 <= m, n <= 50", "grid[i][j] is 0 or 1"],
    "testCases": ["[[1]] -> 1", "[[0]] -> 0", "[[1,1],[1,0]] -> 3"],
    "targetMinutes": 20,
    "starterCode": "public int maxAreaOfIsland(int[][] grid) {\n    // DFS from each '1': return 1 + area(4 directions)\n    // Mark visited by setting to 0\n    return 0;\n}"
  },
  {
    "id": "dsa_pacific_atlantic", "category": "DSA", "difficulty": "Medium",
    "title": "Pacific Atlantic Water Flow",
    "statement": "Given an m x n matrix of non-negative integers representing heights, water can flow to adjacent cells with equal or smaller height. Find all cells from which water can flow to both the Pacific ocean (top/left borders) and Atlantic ocean (bottom/right borders).",
    "examples": ["[[1,2,2,3,5],[3,2,3,4,4],[2,4,5,3,1],[6,7,1,4,5],[5,1,1,2,4]] -> [[0,4],[1,3],[1,4],[2,2],[3,0],[3,1],[4,0]]"],
    "constraints": ["m == heights.length", "n == heights[i].length", "1 <= m, n <= 200"],
    "testCases": ["1x1 matrix -> [[0,0]]"],
    "targetMinutes": 35,
    "starterCode": "public List<List<Integer>> pacificAtlantic(int[][] heights) {\n    // Reverse BFS: start from ocean borders, mark reachable cells\n    // Result = intersection of pacific-reachable and atlantic-reachable\n    return new ArrayList<>();\n}"
  },
  {
    "id": "dsa_surrounded_regions", "category": "DSA", "difficulty": "Medium",
    "title": "Surrounded Regions",
    "statement": "Given an m x n matrix board with 'X' and 'O', capture all regions surrounded by 'X'. A region is captured by flipping all 'O's into 'X's in that surrounded region. 'O's on borders and connected to borders are NOT captured.",
    "examples": ["[['X','X','X','X'],['X','O','O','X'],['X','X','O','X'],['X','O','X','X']] -> flip inner O's to X"],
    "constraints": ["m == board.length", "n == board[i].length", "1 <= m, n <= 200"],
    "testCases": ["all X's -> no change", "O on border -> stays"],
    "targetMinutes": 30,
    "starterCode": "public void solve(char[][] board) {\n    // Step 1: BFS/DFS from all border 'O's, mark as safe (e.g., 'S')\n    // Step 2: flip remaining 'O' to 'X', flip 'S' back to 'O'\n}"
  },
  {
    "id": "dsa_rotting_oranges", "category": "DSA", "difficulty": "Medium",
    "title": "Rotting Oranges",
    "statement": "In a grid, 0=empty, 1=fresh orange, 2=rotten orange. Each minute, any fresh orange adjacent to a rotten orange becomes rotten. Return the minimum minutes until no fresh orange remains. If impossible, return -1.",
    "examples": ["[[2,1,1],[1,1,0],[0,1,1]] -> 4", "[[2,1,1],[0,1,1],[1,0,1]] -> -1", "[[0,2]] -> 0"],
    "constraints": ["1 <= m, n <= 10", "grid[i][j] is 0, 1, or 2"],
    "testCases": ["[[2]] -> 0", "[[1]] -> -1", "[[0,1]] -> -1"],
    "targetMinutes": 25,
    "starterCode": "public int orangesRotting(int[][] grid) {\n    // Multi-source BFS from all rotten oranges\n    // Count fresh oranges. Each BFS level = 1 minute\n    // Return -1 if fresh > 0 after BFS\n    return 0;\n}"
  },
  {
    "id": "dsa_course_schedule", "category": "DSA", "difficulty": "Medium",
    "title": "Course Schedule (Cycle Detection)",
    "statement": "You have numCourses courses labeled 0 to n-1 and a list of prerequisites [a,b] meaning you must take b before a. Determine if it's possible to finish all courses (i.e., no cycle exists in the prerequisite graph).",
    "examples": ["numCourses=2, prerequisites=[[1,0]] -> true", "numCourses=2, prerequisites=[[1,0],[0,1]] -> false"],
    "constraints": ["1 <= numCourses <= 2000", "0 <= prerequisites.length <= 5000", "prerequisites[i].length == 2"],
    "testCases": ["0 prerequisites -> true", "self-loop -> false"],
    "targetMinutes": 25,
    "starterCode": "public boolean canFinish(int numCourses, int[][] prerequisites) {\n    // Build adjacency list. Topological sort (Kahn's BFS) or DFS cycle detection\n    // If topological sort includes all nodes, no cycle -> return true\n    return false;\n}"
  },
  {
    "id": "dsa_course_schedule_ii", "category": "DSA", "difficulty": "Medium",
    "title": "Course Schedule II (Topological Sort)",
    "statement": "Given numCourses and prerequisites, return the ordering of courses you should take to finish all courses. If impossible (cycle), return empty array.",
    "examples": ["numCourses=2, [[1,0]] -> [0,1]", "numCourses=4, [[1,0],[2,0],[3,1],[3,2]] -> [0,2,1,3]", "cyclic -> []"],
    "constraints": ["1 <= numCourses <= 2000", "0 <= prerequisites.length <= numCourses*(numCourses-1)"],
    "testCases": ["1 course, no prereqs -> [0]", "cycle -> []"],
    "targetMinutes": 30,
    "starterCode": "public int[] findOrder(int numCourses, int[][] prerequisites) {\n    // Kahn's algorithm: BFS with in-degree array\n    // Add all 0-in-degree nodes to queue, process and reduce neighbors' in-degree\n    return new int[]{};\n}"
  },
  {
    "id": "dsa_redundant_connection", "category": "DSA", "difficulty": "Medium",
    "title": "Redundant Connection (Union-Find)",
    "statement": "In an undirected graph with n nodes labeled 1 to n, one extra edge was added to a tree. Find and return that extra edge. If there are multiple answers, return the edge that occurs last in the input.",
    "examples": ["edges=[[1,2],[1,3],[2,3]] -> [2,3]", "edges=[[1,2],[2,3],[3,4],[1,4],[1,5]] -> [1,4]"],
    "constraints": ["n == edges.length", "3 <= n <= 1000", "edges[i] is a valid edge"],
    "testCases": ["[[1,2],[2,3],[1,3]] -> [1,3]"],
    "targetMinutes": 30,
    "starterCode": "public int[] findRedundantConnection(int[][] edges) {\n    // Union-Find (DSU): for each edge, if same component -> redundant\n    // parent[] and rank[] arrays, find() with path compression\n    return new int[]{};\n}"
  },
  {
    "id": "dsa_word_ladder", "category": "DSA", "difficulty": "Hard",
    "title": "Word Ladder",
    "statement": "Given two words beginWord and endWord, and a word list, return the number of words in the shortest transformation sequence from beginWord to endWord. Each transformation changes exactly one letter, and every intermediate word must be in the word list.",
    "examples": ["beginWord=hit, endWord=cog, wordList=[hot,dot,dog,lot,log,cog] -> 5", "endWord not in list -> 0"],
    "constraints": ["1 <= beginWord.length <= 10", "endWord is in wordList for valid case", "1 <= wordList.length <= 5000"],
    "testCases": ["same word -> 1", "no path -> 0"],
    "targetMinutes": 40,
    "starterCode": "public int ladderLength(String beginWord, String endWord, List<String> wordList) {\n    // BFS: try changing each character position to a-z\n    // If result is in wordSet and not visited, add to queue\n    // Return level count when endWord found\n    return 0;\n}"
  },

  # ── DYNAMIC PROGRAMMING (Days 67-75) ─────────────────────────────────────────
  {
    "id": "dsa_climbing_stairs", "category": "DSA", "difficulty": "Easy",
    "title": "Climbing Stairs",
    "statement": "You are climbing a staircase with n steps. Each time you can climb 1 or 2 steps. How many distinct ways can you climb to the top? This is essentially the Fibonacci sequence.",
    "examples": ["n=2 -> 2 (1+1, 2)", "n=3 -> 3 (1+1+1, 1+2, 2+1)"],
    "constraints": ["1 <= n <= 45"],
    "testCases": ["n=1 -> 1", "n=4 -> 5", "n=5 -> 8"],
    "targetMinutes": 15,
    "starterCode": "public int climbStairs(int n) {\n    // dp[i] = dp[i-1] + dp[i-2]\n    // dp[1]=1, dp[2]=2\n    // Or just track two variables (space O(1))\n    return 0;\n}"
  },
  {
    "id": "dsa_min_cost_climbing", "category": "DSA", "difficulty": "Easy",
    "title": "Min Cost Climbing Stairs",
    "statement": "Given an integer array cost where cost[i] is the cost of the ith step. Once you pay the cost, you can climb one or two steps. You can start from step 0 or step 1. Return the minimum cost to reach the top (beyond last step).",
    "examples": ["[10,15,20] -> 15", "[1,100,1,1,1,100,1,1,100,1] -> 6"],
    "constraints": ["2 <= cost.length <= 1000", "0 <= cost[i] <= 999"],
    "testCases": ["[0,0] -> 0", "[1,2,3] -> 2"],
    "targetMinutes": 15,
    "starterCode": "public int minCostClimbingStairs(int[] cost) {\n    // dp[i] = cost[i] + min(dp[i-1], dp[i-2])\n    // Answer = min(dp[n-1], dp[n-2])\n    return 0;\n}"
  },
  {
    "id": "dsa_house_robber", "category": "DSA", "difficulty": "Medium",
    "title": "House Robber",
    "statement": "You are a robber. Given an array representing money in each house, you cannot rob two adjacent houses. Find the maximum money you can rob tonight without alerting the police.",
    "examples": ["[1,2,3,1] -> 4 (rob house 1 and 3)", "[2,7,9,3,1] -> 12 (rob house 1,3,5)"],
    "constraints": ["1 <= nums.length <= 100", "0 <= nums[i] <= 400"],
    "testCases": ["[1] -> 1", "[2,1] -> 2", "[0,0,0] -> 0"],
    "targetMinutes": 20,
    "starterCode": "public int rob(int[] nums) {\n    // dp[i] = max(dp[i-1], dp[i-2] + nums[i])\n    // Track only two variables: prev1 (rob i-1), prev2 (rob i-2)\n    return 0;\n}"
  },
  {
    "id": "dsa_house_robber_ii", "category": "DSA", "difficulty": "Medium",
    "title": "House Robber II",
    "statement": "Houses are arranged in a circle. The first and last house are adjacent. You cannot rob adjacent houses. Find the maximum money you can rob. All houses in a circle.",
    "examples": ["[2,3,2] -> 3", "[1,2,3,1] -> 4", "[1,2,3] -> 3"],
    "constraints": ["1 <= nums.length <= 100", "0 <= nums[i] <= 1000"],
    "testCases": ["[1] -> 1", "[2,1,1,2] -> 4"],
    "targetMinutes": 25,
    "starterCode": "public int rob(int[] nums) {\n    // Run House Robber I on nums[0..n-2] and nums[1..n-1]\n    // Return max of both (can't take both first and last)\n    return 0;\n}"
  },
  {
    "id": "dsa_coin_change", "category": "DSA", "difficulty": "Medium",
    "title": "Coin Change",
    "statement": "Given an array of coin denominations and an amount, return the fewest number of coins needed to make up that amount. If it cannot be made, return -1. You have an infinite supply of each coin.",
    "examples": ["coins=[1,5,11], amount=15 -> 3 (5+5+5 or 11+1+1+... wait 11+3=14? No: coins=[1,5,11]: 15=11+? No, 11+4: 11+1+1+1+1=5 coins. Actually 5+5+5=3)", "coins=[2], amount=3 -> -1"],
    "constraints": ["1 <= coins.length <= 12", "1 <= coins[i] <= 2^31-1", "0 <= amount <= 10^4"],
    "testCases": ["coins=[1], amount=0 -> 0", "coins=[1,2,5], amount=11 -> 3 (5+5+1)"],
    "targetMinutes": 25,
    "starterCode": "public int coinChange(int[] coins, int amount) {\n    // dp[i] = min coins to make amount i\n    // dp[0]=0, dp[i]=min over all coins: dp[i-coin]+1\n    // Init dp with amount+1 (infinity)\n    return 0;\n}"
  },
  {
    "id": "dsa_longest_increasing_subseq", "category": "DSA", "difficulty": "Medium",
    "title": "Longest Increasing Subsequence",
    "statement": "Given an integer array nums, return the length of the longest strictly increasing subsequence.",
    "examples": ["[10,9,2,5,3,7,101,18] -> 4 (2,3,7,101)", "[0,1,0,3,2,3] -> 4", "[7,7,7,7,7] -> 1"],
    "constraints": ["1 <= nums.length <= 2500", "-10^4 <= nums[i] <= 10^4"],
    "testCases": ["[1] -> 1", "[1,2] -> 2", "[2,1] -> 1"],
    "targetMinutes": 30,
    "starterCode": "public int lengthOfLIS(int[] nums) {\n    // dp[i] = length of LIS ending at index i\n    // For each i, check all j < i: if nums[j] < nums[i], dp[i] = max(dp[i], dp[j]+1)\n    // O(n^2). Can optimize to O(n log n) with patience sort\n    return 0;\n}"
  },
  {
    "id": "dsa_unique_paths", "category": "DSA", "difficulty": "Medium",
    "title": "Unique Paths",
    "statement": "A robot is on the top-left corner of an m x n grid. It can only move right or down. How many unique paths are there from top-left to bottom-right?",
    "examples": ["m=3, n=7 -> 28", "m=3, n=2 -> 3", "m=7, n=3 -> 28"],
    "constraints": ["1 <= m, n <= 100"],
    "testCases": ["m=1, n=1 -> 1", "m=2, n=2 -> 2", "m=3, n=3 -> 6"],
    "targetMinutes": 20,
    "starterCode": "public int uniquePaths(int m, int n) {\n    // dp[i][j] = dp[i-1][j] + dp[i][j-1]\n    // dp[0][j] = 1, dp[i][0] = 1 (only one way along borders)\n    return 0;\n}"
  },
  {
    "id": "dsa_jump_game", "category": "DSA", "difficulty": "Medium",
    "title": "Jump Game",
    "statement": "Given an integer array nums where nums[i] is the maximum jump length from index i, return true if you can reach the last index starting from index 0.",
    "examples": ["[2,3,1,1,4] -> true", "[3,2,1,0,4] -> false"],
    "constraints": ["1 <= nums.length <= 3*10^4", "0 <= nums[i] <= 10^5"],
    "testCases": ["[0] -> true", "[1,0] -> true", "[1,0,0] -> false"],
    "targetMinutes": 20,
    "starterCode": "public boolean canJump(int[] nums) {\n    // Greedy: track maxReach = max index reachable so far\n    // If current index > maxReach, return false\n    // maxReach = max(maxReach, i + nums[i])\n    return false;\n}"
  },
  {
    "id": "dsa_word_break", "category": "DSA", "difficulty": "Medium",
    "title": "Word Break",
    "statement": "Given a string s and a dictionary of strings wordDict, return true if s can be segmented into a space-separated sequence of one or more dictionary words.",
    "examples": ["s=leetcode, wordDict=[leet,code] -> true", "s=applepenapple, wordDict=[apple,pen] -> true", "s=catsandog, wordDict=[cats,dog,sand,and,cat] -> false"],
    "constraints": ["1 <= s.length <= 300", "1 <= wordDict.length <= 1000"],
    "testCases": ["s=a, wordDict=[a] -> true", "single char not in dict -> false"],
    "targetMinutes": 25,
    "starterCode": "public boolean wordBreak(String s, List<String> wordDict) {\n    // dp[i] = true if s[0..i-1] can be segmented\n    // For each i, check all j < i: if dp[j] && s[j..i] in dict, dp[i]=true\n    return false;\n}"
  },

  # ── BONUS / Days 76-90 (Greedy + Review) ─────────────────────────────────────
  {
    "id": "dsa_flood_fill", "category": "DSA", "difficulty": "Easy",
    "title": "Flood Fill",
    "statement": "Implement the flood fill algorithm. Given an image (2D int array), a starting pixel (sr,sc), and a new color, flood fill the starting pixel and all connected pixels of the same original color.",
    "examples": ["image=[[1,1,1],[1,1,0],[1,0,1]], sr=1, sc=1, color=2 -> [[2,2,2],[2,2,0],[2,0,1]]"],
    "constraints": ["1 <= m, n <= 50", "0 <= image[i][j], color < 2^16"],
    "testCases": ["single pixel -> change its color", "already target color -> no change"],
    "targetMinutes": 20,
    "starterCode": "public int[][] floodFill(int[][] image, int sr, int sc, int color) {\n    // DFS/BFS from (sr,sc). Change all connected same-color pixels.\n    // Guard: if image[sr][sc] == color, return immediately\n    return image;\n}"
  },
  {
    "id": "dsa_num_connected_components", "category": "DSA", "difficulty": "Medium",
    "title": "Number of Connected Components",
    "statement": "Given n nodes labeled 0 to n-1 and an array of undirected edges, return the number of connected components in the graph.",
    "examples": ["n=5, edges=[[0,1],[1,2],[3,4]] -> 2", "n=5, edges=[[0,1],[1,2],[2,3],[3,4]] -> 1"],
    "constraints": ["1 <= n <= 2000", "1 <= edges.length <= 5000", "No repeated edges"],
    "testCases": ["n=1, edges=[] -> 1", "n=3, edges=[] -> 3"],
    "targetMinutes": 25,
    "starterCode": "public int countComponents(int n, int[][] edges) {\n    // Union-Find: initially n components\n    // Each union reduces count by 1 if different components\n    return 0;\n}"
  },
  {
    "id": "dsa_edit_distance", "category": "DSA", "difficulty": "Hard",
    "title": "Edit Distance",
    "statement": "Given two strings word1 and word2, return the minimum number of operations (insert, delete, replace) to convert word1 to word2.",
    "examples": ["word1=horse, word2=ros -> 3", "word1=intention, word2=execution -> 5"],
    "constraints": ["0 <= word1.length, word2.length <= 500", "words consist of lowercase English letters"],
    "testCases": ["word1='', word2='a' -> 1", "same words -> 0"],
    "targetMinutes": 35,
    "starterCode": "public int minDistance(String word1, String word2) {\n    // dp[i][j] = min ops to convert word1[0..i-1] to word2[0..j-1]\n    // If chars equal: dp[i][j] = dp[i-1][j-1]\n    // Else: dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])\n    return 0;\n}"
  },
  {
    "id": "dsa_longest_common_subseq", "category": "DSA", "difficulty": "Medium",
    "title": "Longest Common Subsequence",
    "statement": "Given two strings text1 and text2, return the length of their longest common subsequence. A subsequence is a sequence derived from another by deleting some characters without changing the order.",
    "examples": ["text1=abcde, text2=ace -> 3 (ace)", "text1=abc, text2=abc -> 3", "text1=abc, text2=def -> 0"],
    "constraints": ["1 <= text1.length, text2.length <= 1000", "consists of lowercase letters"],
    "testCases": ["a,a -> 1", "ab,ba -> 1", "abcde,ace -> 3"],
    "targetMinutes": 30,
    "starterCode": "public int longestCommonSubsequence(String text1, String text2) {\n    // dp[i][j] = LCS of text1[0..i-1] and text2[0..j-1]\n    // If text1[i-1]==text2[j-1]: dp[i][j] = dp[i-1][j-1] + 1\n    // Else: dp[i][j] = max(dp[i-1][j], dp[i][j-1])\n    return 0;\n}"
  },
  {
    "id": "dsa_combination_sum", "category": "DSA", "difficulty": "Medium",
    "title": "Combination Sum",
    "statement": "Given an array of distinct integers candidates and a target, return all unique combinations that sum to target. The same number may be used unlimited times. Combinations may be returned in any order.",
    "examples": ["candidates=[2,3,6,7], target=7 -> [[2,2,3],[7]]", "candidates=[2,3,5], target=8 -> [[2,2,2,2],[2,3,3],[3,5]]"],
    "constraints": ["1 <= candidates.length <= 30", "2 <= candidates[i] <= 40", "All candidates are distinct"],
    "testCases": ["candidates=[2], target=1 -> []", "candidates=[1], target=1 -> [[1]]"],
    "targetMinutes": 30,
    "starterCode": "public List<List<Integer>> combinationSum(int[] candidates, int target) {\n    // Backtracking: at each step include candidate or skip\n    // Recursion: combinationSum(start, remaining, current)\n    return new ArrayList<>();\n}"
  },
  {
    "id": "dsa_partition_equal_subset", "category": "DSA", "difficulty": "Medium",
    "title": "Partition Equal Subset Sum",
    "statement": "Given an integer array nums, return true if you can partition the array into two subsets such that the sum of elements in both subsets is equal.",
    "examples": ["[1,5,11,5] -> true (subsets [1,5,5] and [11])", "[1,2,3,5] -> false"],
    "constraints": ["1 <= nums.length <= 200", "1 <= nums[i] <= 100"],
    "testCases": ["[1,1] -> true", "[1,2] -> false", "[2,2,3,5] -> false"],
    "targetMinutes": 30,
    "starterCode": "public boolean canPartition(int[] nums) {\n    // Target = sum/2. If sum is odd, return false.\n    // dp[j] = can we make sum j from subset?\n    // For each num (reverse order): dp[j] |= dp[j-num]\n    return false;\n}"
  },
  {
    "id": "dsa_decode_ways", "category": "DSA", "difficulty": "Medium",
    "title": "Decode Ways",
    "statement": "A message containing letters A-Z is encoded as '1'-'26'. Given a string s containing only digits, return the number of ways to decode it. '0' cannot stand alone.",
    "examples": ["s=12 -> 2 (AB or L)", "s=226 -> 3 (BZ, VF, BBF)", "s=06 -> 0"],
    "constraints": ["1 <= s.length <= 100", "s contains only digits"],
    "testCases": ["s=1 -> 1", "s=10 -> 1", "s=0 -> 0", "s=11 -> 2"],
    "targetMinutes": 25,
    "starterCode": "public int numDecodings(String s) {\n    // dp[i] = ways to decode s[0..i-1]\n    // Single digit: dp[i] += dp[i-1] if s[i-1] != '0'\n    // Two digits: dp[i] += dp[i-2] if s[i-2..i-1] in [10..26]\n    return 0;\n}"
  },
  {
    "id": "dsa_jump_game_ii", "category": "DSA", "difficulty": "Medium",
    "title": "Jump Game II",
    "statement": "Given an array nums where nums[i] is the max jump length from index i, return the minimum number of jumps to reach the last index. Assume you can always reach the last index.",
    "examples": ["[2,3,1,1,4] -> 2 (jump 1 to index 1, then 3 to last)", "[2,3,0,1,4] -> 2"],
    "constraints": ["1 <= nums.length <= 10^4", "0 <= nums[i] <= 1000"],
    "testCases": ["[1] -> 0", "[1,1] -> 1", "[2,1,1] -> 1"],
    "targetMinutes": 25,
    "starterCode": "public int jump(int[] nums) {\n    // Greedy: track current window [l, r]\n    // Expand to farthest reachable from [l,r]\n    // Increment jumps, move l=r+1, r=farthest\n    return 0;\n}"
  },
  {
    "id": "dsa_meeting_rooms", "category": "DSA", "difficulty": "Easy",
    "title": "Meeting Rooms",
    "statement": "Given an array of meeting time intervals where intervals[i] = [start, end], determine if a person could attend all meetings (no overlapping intervals).",
    "examples": ["[[0,30],[5,10],[15,20]] -> false", "[[7,10],[2,4]] -> true"],
    "constraints": ["0 <= intervals.length <= 5*10^4"],
    "testCases": ["[] -> true", "[[1,2]] -> true"],
    "targetMinutes": 15,
    "starterCode": "public boolean canAttendMeetings(int[][] intervals) {\n    // Sort by start time\n    // Check if any intervals[i][0] < intervals[i-1][1]\n    return false;\n}"
  },
  {
    "id": "dsa_missing_number", "category": "DSA", "difficulty": "Easy",
    "title": "Missing Number",
    "statement": "Given an array nums containing n distinct numbers in the range [0, n], return the only number in the range that is missing from the array.",
    "examples": ["[3,0,1] -> 2", "[0,1] -> 2", "[9,6,4,2,3,5,7,0,1] -> 8"],
    "constraints": ["n == nums.length", "1 <= n <= 10^4", "All nums are distinct and in [0,n]"],
    "testCases": ["[0] -> 1", "[1] -> 0"],
    "targetMinutes": 15,
    "starterCode": "public int missingNumber(int[] nums) {\n    // Expected sum = n*(n+1)/2\n    // Missing = expectedSum - actualSum\n    // Or use XOR: XOR all indices and values\n    return 0;\n}"
  },
]
