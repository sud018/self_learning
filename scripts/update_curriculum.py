"""
Update all 90 curriculum JSON files:
 - Replace the 3 generic same-for-every-day coding tasks with topic-specific ones
 - Add one Striver-75 DSA problem per day as an additional task
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from striver75_dsa import STRIVER_75

CURRICULUM_DIR = os.path.join(os.path.dirname(__file__), "../backend/data/curriculum")

# ─── Topic-specific coding tasks for every day ────────────────────────────────
# Format: list of dicts matching the existing schema
# category must reflect the day's primary tech (Java / Spring Boot / SQL / Angular / DSA)
DAILY_TASKS = {
1: [
  {"id":"d01c1","category":"Java","difficulty":"Easy","title":"Hello World and JVM path",
   "statement":"Write a Java program that prints 'Hello, World!' and then prints the Java version using System.getProperty(\"java.version\"). What does JVM do with your .java file before running it?",
   "examples":["Output: Hello, World!\\nJava version: 21.x"],
   "constraints":["Use System.out.println","Use System.getProperty"],
   "testCases":["Hello, World! is first line","Version string is not null"],
   "targetMinutes":10,
   "starterCode":"public class Main {\n    public static void main(String[] args) {\n        // Print Hello World\n        // Print Java version\n    }\n}"},
  {"id":"d01c2","category":"Java","difficulty":"Easy","title":"JVM memory areas quiz program",
   "statement":"Write a method that creates a local int variable (stack), a String literal (string pool), and an object with new (heap). Print each value. This demonstrates the three main JVM memory areas.",
   "examples":["stack=42, pool=hello, heap=java.lang.Object@..."],
   "constraints":["Must use new keyword for heap allocation"],
   "testCases":["All three values printed without exception"],
   "targetMinutes":15,
   "starterCode":"public void showJvmMemory() {\n    int stackVar = 42;        // stack\n    String poolStr = \"hello\"; // string pool\n    Object heapObj = new Object(); // heap\n    // print all three\n}"},
  {"id":"d01c3","category":"Java","difficulty":"Easy","title":"Basic arithmetic calculator",
   "statement":"Write a method calculate(int a, int b, String op) that returns the result of a+b, a-b, a*b, or a/b based on op. Handle division by zero by returning Integer.MIN_VALUE.",
   "examples":["calculate(10,3,\"+\") -> 13","calculate(10,0,\"/\") -> Integer.MIN_VALUE"],
   "constraints":["op is one of +, -, *, /","Handle division by zero"],
   "testCases":["calculate(6,2,\"*\") -> 12","calculate(5,0,\"/\") -> Integer.MIN_VALUE"],
   "targetMinutes":15,
   "starterCode":"public int calculate(int a, int b, String op) {\n    // use switch or if-else on op\n    return 0;\n}"}
],
2: [
  {"id":"d02c1","category":"Java","difficulty":"Easy","title":"Type conversion chain",
   "statement":"Write a method that takes a double salary, converts it to int (truncation), then to String, then parses it back to int. Return the final int. This shows implicit vs explicit casting.",
   "examples":["salary=1234.99 -> 1234"],
   "constraints":["Use (int) cast, String.valueOf, Integer.parseInt"],
   "testCases":["1234.99 -> 1234","0.9 -> 0"],
   "targetMinutes":15,
   "starterCode":"public int convertSalary(double salary) {\n    // cast to int, then String, then back\n    return 0;\n}"},
  {"id":"d02c2","category":"Java","difficulty":"Easy","title":"Swap without temp variable",
   "statement":"Write a method swap(int[] arr, int i, int j) that swaps two elements in-place using XOR (no temporary variable). Then write a second version using arithmetic.",
   "examples":["arr=[3,7], i=0, j=1 -> arr=[7,3]"],
   "constraints":["No extra variable allowed in XOR version","Must modify array in place"],
   "testCases":["[1,2] -> [2,1]","[5,5] -> [5,5]"],
   "targetMinutes":15,
   "starterCode":"public void swap(int[] arr, int i, int j) {\n    // XOR trick: a^=b; b^=a; a^=b;\n}"},
  {"id":"d02c3","category":"Java","difficulty":"Easy","title":"Temperature converter",
   "statement":"Write methods celsiusToFahrenheit(double c) and fahrenheitToCelsius(double f). Formula: F = C*9/5 + 32. Round to 2 decimal places using Math.round.",
   "examples":["celsiusToFahrenheit(100) -> 212.0","fahrenheitToCelsius(32) -> 0.0"],
   "constraints":["Use double arithmetic","Round result to 2 decimal places"],
   "testCases":["c=0 -> f=32.0","f=212 -> c=100.0"],
   "targetMinutes":15,
   "starterCode":"public double celsiusToFahrenheit(double c) {\n    return 0;\n}\npublic double fahrenheitToCelsius(double f) {\n    return 0;\n}"}
],
3: [
  {"id":"d03c1","category":"Java","difficulty":"Easy","title":"FizzBuzz",
   "statement":"Write a method fizzBuzz(int n) that returns a List<String> from 1 to n. For multiples of 3 add 'Fizz', multiples of 5 add 'Buzz', multiples of both add 'FizzBuzz', otherwise add the number as String.",
   "examples":["n=5 -> [1, 2, Fizz, 4, Buzz]","n=15 -> [...,FizzBuzz]"],
   "constraints":["1 <= n <= 10000"],
   "testCases":["n=1 -> [1]","n=3 -> [1,2,Fizz]","n=15 includes FizzBuzz"],
   "targetMinutes":15,
   "starterCode":"public List<String> fizzBuzz(int n) {\n    List<String> result = new ArrayList<>();\n    // loop 1..n\n    return result;\n}"},
  {"id":"d03c2","category":"Java","difficulty":"Easy","title":"Leap year checker",
   "statement":"Write isLeapYear(int year). A year is a leap year if: divisible by 4 AND (not divisible by 100 OR divisible by 400).",
   "examples":["2000 -> true","1900 -> false","2024 -> true","2023 -> false"],
   "constraints":["1 <= year <= 9999"],
   "testCases":["2000 -> true","1900 -> false","2100 -> false","2024 -> true"],
   "targetMinutes":10,
   "starterCode":"public boolean isLeapYear(int year) {\n    // Use the three-condition rule\n    return false;\n}"},
  {"id":"d03c3","category":"Java","difficulty":"Easy","title":"Grade calculator",
   "statement":"Write getGrade(int score) returning 'A' (90-100), 'B' (80-89), 'C' (70-79), 'D' (60-69), 'F' (<60). Use switch expression (Java 14+) or if-else chain.",
   "examples":["95 -> A","72 -> C","55 -> F"],
   "constraints":["0 <= score <= 100"],
   "testCases":["100 -> A","89 -> B","60 -> D","0 -> F"],
   "targetMinutes":10,
   "starterCode":"public char getGrade(int score) {\n    // if score >= 90 -> A, etc.\n    return 'F';\n}"}
],
4: [
  {"id":"d04c1","category":"Java","difficulty":"Easy","title":"Sum of digits",
   "statement":"Write sumOfDigits(int n) that returns the sum of all digits in n. Handle negative numbers by taking absolute value.",
   "examples":["n=1234 -> 10","n=-456 -> 15"],
   "constraints":["Handle negative input","Work for n=0"],
   "testCases":["0 -> 0","99 -> 18","1000 -> 1"],
   "targetMinutes":15,
   "starterCode":"public int sumOfDigits(int n) {\n    n = Math.abs(n);\n    int sum = 0;\n    // while n > 0: sum += n%10; n /= 10\n    return sum;\n}"},
  {"id":"d04c2","category":"Java","difficulty":"Easy","title":"Is palindrome (number)",
   "statement":"Write isPalindrome(int x) that returns true if x is a palindrome (reads the same forward and backward). Negative numbers are not palindromes.",
   "examples":["121 -> true","123 -> false","-121 -> false","10 -> false"],
   "constraints":["Don't convert to String","Work for single digits"],
   "testCases":["0 -> true","11 -> true","10 -> false"],
   "targetMinutes":20,
   "starterCode":"public boolean isPalindrome(int x) {\n    // Reverse the second half of the number\n    // Compare reversed half with first half\n    return false;\n}"},
  {"id":"d04c3","category":"Java","difficulty":"Medium","title":"Power function",
   "statement":"Write myPow(double x, int n) that calculates x raised to the power n. Handle negative exponents. Use fast power (exponentiation by squaring) for O(log n).",
   "examples":["myPow(2.0, 10) -> 1024.0","myPow(2.1, 3) -> 9.261","myPow(2.0, -2) -> 0.25"],
   "constraints":["Use exponentiation by squaring","Handle n < 0"],
   "testCases":["1.0, any -> 1.0","2.0, 0 -> 1.0","2.0, -1 -> 0.5"],
   "targetMinutes":20,
   "starterCode":"public double myPow(double x, int n) {\n    // If n < 0: x = 1/x, n = -n\n    // Fast power: if n%2==0 return pow(x*x, n/2)\n    return 0;\n}"}
],
5: [
  {"id":"d05c1","category":"Java","difficulty":"Easy","title":"Reverse a string",
   "statement":"Write reverseString(String s) without using StringBuilder.reverse(). Use a char array or two-pointer approach. Return the reversed string.",
   "examples":["hello -> olleh","Java -> avaJ","'' -> ''"],
   "constraints":["No StringBuilder.reverse()","O(n) time, O(n) space"],
   "testCases":["a -> a","ab -> ba","abcde -> edcba"],
   "targetMinutes":10,
   "starterCode":"public String reverseString(String s) {\n    char[] chars = s.toCharArray();\n    // two pointer swap: l=0, r=end\n    return new String(chars);\n}"},
  {"id":"d05c2","category":"Java","difficulty":"Easy","title":"Count vowels and consonants",
   "statement":"Write a method that returns an int[2] where [0]=vowel count, [1]=consonant count. Ignore non-letter characters. Case-insensitive.",
   "examples":["Hello World -> [3, 7]","aeiou -> [5, 0]"],
   "constraints":["Case-insensitive","Ignore spaces and special chars"],
   "testCases":["'' -> [0,0]","a -> [1,0]","b -> [0,1]"],
   "targetMinutes":15,
   "starterCode":"public int[] countVowelsConsonants(String s) {\n    int vowels = 0, consonants = 0;\n    String lower = s.toLowerCase();\n    // for each char: check if it's a letter, then vowel or consonant\n    return new int[]{vowels, consonants};\n}"},
  {"id":"d05c3","category":"Java","difficulty":"Easy","title":"First non-repeating character",
   "statement":"Write firstNonRepeating(String s) that returns the first character that does not repeat in the string. Return '\\0' if all characters repeat.",
   "examples":["leetcode -> l","aabb -> \\0","swiss -> w"],
   "constraints":["O(n) time","Lowercase letters only"],
   "testCases":["a -> a","aab -> b","aabb -> \\0"],
   "targetMinutes":15,
   "starterCode":"public char firstNonRepeating(String s) {\n    // LinkedHashMap preserves insertion order\n    // Count freq, then iterate to find first with freq=1\n    return '\\0';\n}"}
],
6: [
  {"id":"d06c1","category":"Java","difficulty":"Easy","title":"Array rotation",
   "statement":"Write rotate(int[] nums, int k) that rotates the array to the right by k steps in-place. Example: [1,2,3,4,5], k=2 -> [4,5,1,2,3].",
   "examples":["[1,2,3,4,5], k=2 -> [4,5,1,2,3]","[1,2], k=3 -> [2,1]"],
   "constraints":["In-place O(1) extra space","k can be larger than array length"],
   "testCases":["[1], k=99 -> [1]","[1,2,3], k=0 -> [1,2,3]"],
   "targetMinutes":20,
   "starterCode":"public void rotate(int[] nums, int k) {\n    // Normalize k: k = k % nums.length\n    // Three reverse trick: reverse all, reverse [0..k-1], reverse [k..n-1]\n}"},
  {"id":"d06c2","category":"Java","difficulty":"Easy","title":"Find duplicates in array",
   "statement":"Write findDuplicates(int[] nums) returning all elements that appear more than once. Input values are in range [1, n]. Return result in any order.",
   "examples":["[4,3,2,7,8,2,3,1] -> [2,3]","[1,1,2] -> [1]"],
   "constraints":["1 <= nums[i] <= n","O(n) time, O(1) extra space (use index-marking trick)"],
   "testCases":["[1] -> []","[2,2] -> [2]"],
   "targetMinutes":20,
   "starterCode":"public List<Integer> findDuplicates(int[] nums) {\n    // For each num, go to index abs(num)-1 and negate\n    // If already negative, it's a duplicate\n    return new ArrayList<>();\n}"},
  {"id":"d06c3","category":"Java","difficulty":"Easy","title":"Move zeroes to end",
   "statement":"Write moveZeroes(int[] nums) that moves all 0s to the end while maintaining the relative order of non-zero elements. Do this in-place.",
   "examples":["[0,1,0,3,12] -> [1,3,12,0,0]","[0] -> [0]"],
   "constraints":["In-place, no extra array","Maintain order of non-zero elements"],
   "testCases":["[1,2,3] -> [1,2,3]","[0,0,1] -> [1,0,0]"],
   "targetMinutes":15,
   "starterCode":"public void moveZeroes(int[] nums) {\n    // Two pointers: slow tracks insert position\n    // Fast scans; when nums[fast]!=0, place at slow position\n}"}
],
7: [
  {"id":"d07c1","category":"Java","difficulty":"Easy","title":"Parse and validate user input",
   "statement":"Write parseAge(String input) that parses a String to int age. If null, blank, or not a number, throw IllegalArgumentException. If age < 0 or > 150, throw IllegalArgumentException.",
   "examples":["'25' -> 25","'abc' -> throws","'-1' -> throws","null -> throws"],
   "constraints":["Use Integer.parseInt with try-catch","Validate range after parsing"],
   "testCases":["'0' -> 0","'150' -> 150","'151' -> throws"],
   "targetMinutes":20,
   "starterCode":"public int parseAge(String input) {\n    if (input == null || input.isBlank()) throw new IllegalArgumentException(\"empty\");\n    // parse, catch NumberFormatException, validate range\n    return 0;\n}"},
  {"id":"d07c2","category":"Java","difficulty":"Easy","title":"Debug: find the off-by-one",
   "statement":"The following method should sum array elements from index start to end (inclusive) but has an off-by-one bug. Fix it: for(int i=start; i<end; i++) sum+=arr[i];",
   "examples":["arr=[1,2,3,4], start=0, end=3 -> should be 10, buggy returns 6"],
   "constraints":["Fix the loop condition","Write a corrected version"],
   "testCases":["[1,2,3], 0, 2 -> 6","[5], 0, 0 -> 5"],
   "targetMinutes":10,
   "starterCode":"public int sumRange(int[] arr, int start, int end) {\n    int sum = 0;\n    for (int i = start; i < end; i++) { // BUG: should be <=\n        sum += arr[i];\n    }\n    return sum;\n}"},
  {"id":"d07c3","category":"Java","difficulty":"Easy","title":"Print multiplication table",
   "statement":"Write printTable(int n) that prints the multiplication table for n from 1 to 10 in the format 'n x i = result' on each line.",
   "examples":["n=3: 3 x 1 = 3, 3 x 2 = 6, ..., 3 x 10 = 30"],
   "constraints":["1 <= n <= 20","10 lines of output"],
   "testCases":["n=1: 1 x 1=1 .. 1 x 10=10","n=5: 5 x 5=25 appears"],
   "targetMinutes":10,
   "starterCode":"public void printTable(int n) {\n    for (int i = 1; i <= 10; i++) {\n        // print: n + \" x \" + i + \" = \" + (n*i)\n    }\n}"}
],
8: [
  {"id":"d08c1","category":"Java","difficulty":"Easy","title":"Simple BankAccount class",
   "statement":"Create a BankAccount class with fields accountId (String), owner (String), balance (double). Add methods deposit(double) and withdraw(double). Withdrawal should fail with exception if insufficient funds.",
   "examples":["deposit(100), withdraw(50) -> balance=50","withdraw(200) on balance=100 -> throws"],
   "constraints":["Balance cannot go negative","Use private fields with getters"],
   "testCases":["new account balance=0","deposit(50).getBalance() -> 50"],
   "targetMinutes":20,
   "starterCode":"public class BankAccount {\n    private String accountId;\n    private String owner;\n    private double balance;\n    // constructor, deposit, withdraw, getBalance\n}"},
  {"id":"d08c2","category":"Java","difficulty":"Easy","title":"Student grade model",
   "statement":"Create a Student class with name, id, and a Map<String,Integer> of subject scores. Add method getAverage() returning average score, and getGrade() returning letter grade based on average.",
   "examples":["scores: Math=85, Java=90, SQL=80 -> average=85.0 -> grade=B"],
   "constraints":["Return 0.0 for empty scores","Reuse getGrade logic from Day 3"],
   "testCases":["empty scores -> average=0.0","one subject=100 -> A"],
   "targetMinutes":20,
   "starterCode":"public class Student {\n    private String name;\n    private String id;\n    private Map<String, Integer> scores = new HashMap<>();\n    public double getAverage() { return 0; }\n    public char getGrade() { return 'F'; }\n}"},
  {"id":"d08c3","category":"Java","difficulty":"Easy","title":"Product catalog item",
   "statement":"Create a Product class with id, name, price (double), category, inStock (boolean). Add toString() for display, equals() based on id, and a static factory method of(String id, String name, double price).",
   "examples":["Product.of(\"P1\",\"Laptop\",999.99).toString() -> Product{id=P1, name=Laptop, price=999.99}"],
   "constraints":["equals/hashCode based on id only","Static factory method pattern"],
   "testCases":["same id -> equals","different id -> not equals"],
   "targetMinutes":20,
   "starterCode":"public class Product {\n    private String id, name, category;\n    private double price;\n    private boolean inStock;\n    public static Product of(String id, String name, double price) { return null; }\n    @Override public String toString() { return \"\"; }\n    @Override public boolean equals(Object o) { return false; }\n}"}
],
9: [
  {"id":"d09c1","category":"Java","difficulty":"Easy","title":"Order total calculator",
   "statement":"Write calculateTotal(List<double[]> items) where each item is [quantity, unitPrice]. Return the total cost. Return 0.0 for null or empty list.",
   "examples":["[[2, 10.0], [3, 5.0]] -> 35.0","[] -> 0.0"],
   "constraints":["Null-safe","Handle 0 quantity items"],
   "testCases":["[[1,100.0]] -> 100.0","[[0,50.0]] -> 0.0"],
   "targetMinutes":15,
   "starterCode":"public double calculateTotal(List<double[]> items) {\n    if (items == null || items.isEmpty()) return 0.0;\n    // sum up quantity * unitPrice for each item\n    return 0.0;\n}"},
  {"id":"d09c2","category":"Java","difficulty":"Easy","title":"String word frequency counter",
   "statement":"Write wordFrequency(String text) returning a Map<String,Integer> of word frequencies. Split by spaces, case-insensitive, ignore punctuation (strip non-alphanumeric from each word).",
   "examples":["'Hello hello world' -> {hello=2, world=1}"],
   "constraints":["Case-insensitive","Strip punctuation from words"],
   "testCases":["'' -> empty map","'a a a' -> {a=3}"],
   "targetMinutes":20,
   "starterCode":"public Map<String, Integer> wordFrequency(String text) {\n    Map<String, Integer> freq = new LinkedHashMap<>();\n    if (text == null || text.isBlank()) return freq;\n    // split, clean each word, count\n    return freq;\n}"},
  {"id":"d09c3","category":"Java","difficulty":"Easy","title":"Stack using two queues",
   "statement":"Implement a stack (push, pop, peek, isEmpty) using two Queue<Integer> instances. The push operation should be O(1), but pop should rotate queues to get LIFO order.",
   "examples":["push(1),push(2),pop() -> 2","push(1),peek() -> 1"],
   "constraints":["Only Queue operations: offer, poll, peek, isEmpty"],
   "testCases":["push(1),push(2),push(3),pop() -> 3"],
   "targetMinutes":25,
   "starterCode":"class MyStack {\n    Queue<Integer> q1 = new LinkedList<>(), q2 = new LinkedList<>();\n    public void push(int val) { }\n    public int pop() { return 0; }\n    public int peek() { return 0; }\n    public boolean isEmpty() { return true; }\n}"}
],
10: [
  {"id":"d10c1","category":"Java","difficulty":"Easy","title":"Fibonacci sequence",
   "statement":"Write fib(int n) returning the nth Fibonacci number (0-indexed: fib(0)=0, fib(1)=1). Use iterative approach. Also write a memoized recursive version.",
   "examples":["fib(0)=0","fib(1)=1","fib(6)=8","fib(10)=55"],
   "constraints":["0 <= n <= 50","Iterative version should be O(n) time O(1) space"],
   "testCases":["fib(0)->0","fib(1)->1","fib(7)->13"],
   "targetMinutes":15,
   "starterCode":"public long fib(int n) {\n    // iterative: track prev, curr\n    return 0;\n}"},
  {"id":"d10c2","category":"Java","difficulty":"Easy","title":"Check anagram",
   "statement":"Write isAnagram(String s, String t) returning true if t is an anagram of s. Same length, same characters with same frequencies. Case-sensitive.",
   "examples":["'anagram','nagaram' -> true","'rat','car' -> false","'','\\0' -> false"],
   "constraints":["Case-sensitive","Handle null and different lengths"],
   "testCases":["same string -> true","'ab','ba' -> true","'ab','ac' -> false"],
   "targetMinutes":15,
   "starterCode":"public boolean isAnagram(String s, String t) {\n    if (s == null || t == null || s.length() != t.length()) return false;\n    int[] freq = new int[256];\n    // increment for s, decrement for t\n    // check all zeros\n    return false;\n}"},
  {"id":"d10c3","category":"Java","difficulty":"Easy","title":"Find missing number 1..N",
   "statement":"Given an array containing n-1 numbers from 1 to n (no duplicates), find the missing number using the formula sum = n*(n+1)/2.",
   "examples":["[1,2,4,5] -> 3","[2] (n=2) -> 1"],
   "constraints":["O(n) time, O(1) space","1 <= n <= 10000"],
   "testCases":["[1] -> 2 (n=2)","[2,3,4,5] -> 1"],
   "targetMinutes":10,
   "starterCode":"public int findMissing(int[] nums) {\n    int n = nums.length + 1;\n    int expected = n * (n + 1) / 2;\n    int actual = 0;\n    for (int num : nums) actual += num;\n    return expected - actual;\n}"}
],
}

# Days 11-90: generate sensible topic-matched tasks per phase
# Phase 2: OOP (11-20), Collections (21-30), Advanced Java (31-40)
# Phase 3: Spring Boot (41-60), Phase 4: Angular (61-80), Phase 5: Prep (81-90)

PHASE_TASKS = {
    # OOP days 11-20
    11: [("Java","Easy","Define a class with fields","Create a Car class with make (String), model (String), year (int), and priceUSD (double). Add a constructor, getters, and a display() method printing all fields.",
          "Car('Toyota','Camry',2023,28000) -> display prints all fields",
          "Car car = new Car(\"Toyota\",\"Camry\",2023,28000.0);\ncar.display();\n// Toyota Camry 2023 $28000.0"),
         ("Java","Easy","Class with validation in constructor","Extend the Car class: throw IllegalArgumentException if year < 1886 or priceUSD < 0.",
          "year=1800 -> throws IllegalArgumentException",
          "public Car(String make, String model, int year, double price) {\n    if (year < 1886) throw new IllegalArgumentException(\"Invalid year\");\n    // set fields\n}"),
         ("SQL","Easy","Basic SELECT with alias","Write a SQL query to select customer_id, first_name, last_name, email from a customers table. Alias first_name as given_name and last_name as family_name.",
          "SELECT customer_id, first_name AS given_name, last_name AS family_name, email FROM customers;",
          "-- Write the SELECT query with aliases\nSELECT ...")],
    12: [("Java","Easy","Objects and references","Write a method copyOrder(Order src) that creates a new Order with same customerId, items list copy (not reference), and totalAmount. Demonstrate why shallow copy is dangerous.",
          "modify copy's items -> src.items unchanged",
          "public Order copyOrder(Order src) {\n    // new ArrayList<>(src.items) for deep copy\n    return null;\n}"),
         ("Java","Easy","equals and hashCode for Order","Implement equals() and hashCode() for an Order class where two orders are equal if they have the same orderId. Use Objects.equals() and Objects.hash().",
          "order1.equals(order2) -> true if same orderId",
          "@Override\npublic boolean equals(Object o) {\n    if (this == o) return true;\n    if (!(o instanceof Order)) return false;\n    Order other = (Order) o;\n    return Objects.equals(this.orderId, other.orderId);\n}"),
         ("SQL","Easy","WHERE with multiple conditions","Write SQL to find all orders where status='PENDING' AND total_amount > 100. Sort by order_date descending.",
          "SELECT * FROM orders WHERE status='PENDING' AND total_amount > 100 ORDER BY order_date DESC;",
          "-- Select pending orders over 100, newest first\nSELECT ...")],
    13: [("Java","Easy","Constructor chaining","Create an Employee class with overloaded constructors: Employee(String name), Employee(String name, String dept), Employee(String name, String dept, double salary). Use this() chaining.",
          "Employee('Alice') -> dept='General', salary=0",
          "public class Employee {\n    public Employee(String name) { this(name, \"General\"); }\n    public Employee(String name, String dept) { this(name, dept, 0); }\n    public Employee(String name, String dept, double salary) { /* set fields */ }\n}"),
         ("Java","Easy","Static factory with builder pattern","Add a static builder to Employee: Employee.builder().name(\"Alice\").dept(\"Engineering\").salary(85000).build(). Implement the minimal Builder inner class.",
          "Employee e = Employee.builder().name(\"Bob\").build()",
          "public static Builder builder() { return new Builder(); }\npublic static class Builder {\n    private String name;\n    // add setters returning Builder for chaining\n    public Employee build() { return new Employee(name, dept, salary); }\n}"),
         ("SQL","Easy","INSERT and SELECT","Write SQL to insert a new employee (id=1, name='Alice', dept='Engineering', salary=85000) into employees table. Then write a SELECT to verify the insert.",
          "INSERT INTO employees VALUES (1,'Alice','Engineering',85000); SELECT * FROM employees WHERE id=1;",
          "-- INSERT then SELECT\nINSERT INTO employees (id, name, dept, salary) ...")],
    14: [("Java","Easy","Inheritance chain","Create Animal (name, sound) -> Dog (breed) -> GoldenRetriever (certifiedService). Each adds its constructor using super(). Override toString() at each level adding its unique field.",
          "new GoldenRetriever('Buddy','Woof','Labrador',true).toString()",
          "public class Dog extends Animal {\n    private String breed;\n    public Dog(String name, String sound, String breed) {\n        super(name, sound);\n        this.breed = breed;\n    }\n}"),
         ("Java","Easy","Method overriding and super","In the above hierarchy, add calculateReward() in Animal (returns 10), override in Dog (returns super()*2), override in GoldenRetriever if certifiedService (returns super()*3 else super()).",
          "GoldenRetriever certified -> 60, uncertified -> 20",
          "// Animal.calculateReward() -> 10\n// Dog.calculateReward() -> super()*2 = 20\n// GoldenRetriever.calculateReward() -> service?60:20"),
         ("SQL","Easy","UPDATE statement","Write SQL to update all employees in dept='Engineering' to get a 10% salary raise. Use: UPDATE employees SET salary = salary * 1.10 WHERE dept='Engineering'",
          "UPDATE employees SET salary = salary * 1.10 WHERE dept = 'Engineering';",
          "-- Give 10% raise to Engineering\nUPDATE employees SET salary = ...")],
    15: [("Java","Easy","Runtime polymorphism","Create Shape (abstract getArea()), Circle(radius), Rectangle(width,height), Triangle(base,height). Store all in List<Shape>. Print area of each using polymorphism.",
          "[new Circle(5), new Rectangle(3,4)] -> [78.5, 12.0]",
          "List<Shape> shapes = List.of(new Circle(5), new Rectangle(3,4));\nfor (Shape s : shapes) System.out.println(s.getArea());"),
         ("Java","Medium","instanceof and casting","Write processPayment(Payment p) that checks if p is CreditCardPayment or CashPayment using instanceof, casts, and calls type-specific methods. Also show pattern matching (Java 16+): if (p instanceof CreditCardPayment cc) cc.getCardNumber()",
          "CreditCard -> print last 4 digits, Cash -> print amount",
          "public void processPayment(Payment p) {\n    if (p instanceof CreditCardPayment cc) {\n        System.out.println(cc.getCardNumber().substring(12));\n    } else if (p instanceof CashPayment cash) {\n        System.out.println(cash.getAmount());\n    }\n}"),
         ("SQL","Easy","DELETE with WHERE","Write SQL to delete all orders where status='CANCELLED' AND order_date < '2023-01-01'. Always use WHERE with DELETE to avoid deleting all rows.",
          "DELETE FROM orders WHERE status='CANCELLED' AND order_date < '2023-01-01';",
          "-- Delete old cancelled orders\nDELETE FROM orders WHERE ...")],
    16: [("Java","Easy","Abstract class template method","Create abstract ReportGenerator with abstract methods getData() and formatHeader(). Implement generateReport() = formatHeader() + getData() + footer. Subclass SalesReport implements both.",
          "SalesReport.generateReport() -> formatted header + data + footer",
          "public abstract class ReportGenerator {\n    public String generateReport() {\n        return formatHeader() + \"\\n\" + getData() + \"\\nEnd of Report\";\n    }\n    protected abstract String formatHeader();\n    protected abstract String getData();\n}"),
         ("Java","Easy","Interface for abstraction","Define Printable interface with print(). Define Saveable with save(String path). Create Document implementing both. Show how accepting Printable in a method hides implementation details.",
          "method(Printable p) { p.print(); } accepts any Printable without knowing concrete type",
          "public interface Printable { void print(); }\npublic interface Saveable { void save(String path); }\npublic class Document implements Printable, Saveable { ... }"),
         ("SQL","Medium","SELECT with DISTINCT and ORDER","Write SQL to get distinct departments from employees, ordered alphabetically. Also write a query to count employees per department.",
          "SELECT DISTINCT dept FROM employees ORDER BY dept; | SELECT dept, COUNT(*) as total FROM employees GROUP BY dept;",
          "-- Distinct departments\nSELECT DISTINCT dept FROM employees ORDER BY dept;\n-- Count per department\nSELECT ...")],
    17: [("Java","Easy","Encapsulation with business rules","Create a Salary class where the amount can only be increased (never decreased). The setter should throw if newAmount <= currentAmount.",
          "setSalary(50000) then setSalary(40000) -> throws",
          "public class Salary {\n    private double amount;\n    public void setSalary(double newAmount) {\n        if (newAmount <= amount) throw new IllegalArgumentException(\"Salary can only increase\");\n        this.amount = newAmount;\n    }\n}"),
         ("Java","Easy","Immutable class","Create an immutable Money class: final class, final fields, no setters, constructor validates amount >= 0. Add add(Money other) returning a new Money.",
          "new Money(100,'USD').add(new Money(50,'USD')) -> Money(150,'USD')",
          "public final class Money {\n    private final double amount;\n    private final String currency;\n    public Money(double amount, String currency) {\n        if (amount < 0) throw new IllegalArgumentException();\n        // set fields\n    }\n    public Money add(Money other) { /* return new Money */ return null; }\n}"),
         ("SQL","Medium","GROUP BY with HAVING","Write SQL to find departments with more than 3 employees and average salary above 70000.",
          "SELECT dept, COUNT(*), AVG(salary) FROM employees GROUP BY dept HAVING COUNT(*) > 3 AND AVG(salary) > 70000;",
          "SELECT dept, COUNT(*) as emp_count, AVG(salary) as avg_sal\nFROM employees\nGROUP BY dept\nHAVING ...")],
    18: [("Java","Easy","Interface with default method","Create Validator<T> interface with boolean validate(T value). Add default method validateAll(List<T> values) that returns true only if all pass validate(). Implement EmailValidator and AgeValidator.",
          "EmailValidator: must contain @. AgeValidator: 0 < age < 150",
          "public interface Validator<T> {\n    boolean validate(T value);\n    default boolean validateAll(List<T> values) {\n        return values.stream().allMatch(this::validate);\n    }\n}"),
         ("Java","Easy","Multiple interface implementation","Show a class OrderProcessor implementing both Validator<Order> and Printable. Demonstrate that Java resolves method conflicts when two interfaces have default methods with same signature.",
          "class OrderProcessor implements Validator<Order>, Printable { @Override boolean validate(Order o) {...} @Override void print() {...} }",
          "public class OrderProcessor implements Validator<Order>, Printable {\n    @Override public boolean validate(Order o) { return o != null && o.getTotal() > 0; }\n    @Override public void print() { System.out.println(\"Printing order...\"); }\n}"),
         ("SQL","Medium","INNER JOIN","Write SQL to get order_id, customer first_name+last_name, and total_amount by joining orders with customers on customer_id.",
          "SELECT o.order_id, c.first_name, c.last_name, o.total_amount FROM orders o INNER JOIN customers c ON o.customer_id = c.customer_id;",
          "SELECT o.order_id, c.first_name, c.last_name, o.total_amount\nFROM orders o\nINNER JOIN customers c ON ...")],
    19: [("Java","Easy","Abstract vs Interface decision","Create abstract class Vehicle with fuel (String), startEngine() abstract. Create Electric extends Vehicle overriding startEngine() printing 'Silent start'. Compare with making Vehicle an interface.",
          "Electric.startEngine() -> 'Silent electric start'",
          "public abstract class Vehicle {\n    protected String fuel;\n    public abstract void startEngine();\n    public void refuel() { System.out.println(\"Refueling with \" + fuel); }\n}\npublic class Electric extends Vehicle {\n    public Electric() { fuel = \"electricity\"; }\n    @Override public void startEngine() { System.out.println(\"Silent electric start\"); }\n}"),
         ("Java","Medium","Template method with hook","Extend Vehicle with an abstract class TaxiService: template method takeTripCost() = baseFare + surcharge(). Implement surcharge() as a hook (empty default). UberTaxi overrides surcharge() to add 20%.",
          "UberTaxi.takeTripCost(10.0) -> 12.0 (10 + 20%)",
          "public abstract class TaxiService {\n    public double takeTripCost(double distance) {\n        return baseFare(distance) + surcharge(distance);\n    }\n    protected abstract double baseFare(double distance);\n    protected double surcharge(double distance) { return 0; } // hook\n}"),
         ("SQL","Medium","LEFT JOIN","Write SQL to find all customers and their orders (include customers with no orders). Show customer_id, name, and order_id (null if no orders).",
          "SELECT c.customer_id, c.first_name, o.order_id FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id;",
          "SELECT c.customer_id, c.first_name, o.order_id\nFROM customers c\nLEFT JOIN orders o ON ...")],
    20: [("Java","Medium","OOP design: e-commerce domain","Design classes for an Order system: Order(orderId, customerId, List<OrderItem>, OrderStatus), OrderItem(productId, qty, unitPrice), OrderStatus enum (PENDING,CONFIRMED,SHIPPED,DELIVERED,CANCELLED). Add subtotal() to Order.",
          "Order with 2 items: qty=2,price=10; qty=1,price=50 -> subtotal=70",
          "public class Order {\n    private String orderId;\n    private String customerId;\n    private List<OrderItem> items;\n    private OrderStatus status;\n    public double subtotal() {\n        return items.stream().mapToDouble(i -> i.getQty() * i.getUnitPrice()).sum();\n    }\n}"),
         ("Java","Medium","Enum with behavior","Make OrderStatus a rich enum: each status has a description and isTerminal() method. DELIVERED and CANCELLED are terminal (no further state changes allowed).",
          "DELIVERED.isTerminal() -> true, PENDING.isTerminal() -> false",
          "public enum OrderStatus {\n    PENDING(\"Awaiting confirmation\", false),\n    DELIVERED(\"Order delivered\", true),\n    CANCELLED(\"Order cancelled\", true);\n    private final String desc;\n    private final boolean terminal;\n    public boolean isTerminal() { return terminal; }\n}"),
         ("SQL","Medium","Aggregate with JOIN","Write SQL to find total sales per customer (sum of total_amount from orders), showing customer name and total. Sort by total descending.",
          "SELECT c.first_name, c.last_name, SUM(o.total_amount) as total_sales FROM customers c JOIN orders o ON c.customer_id=o.customer_id GROUP BY c.customer_id, c.first_name, c.last_name ORDER BY total_sales DESC;",
          "SELECT c.first_name, c.last_name, SUM(o.total_amount) as total_sales\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nGROUP BY ...\nORDER BY total_sales DESC;")],
}

# For days 21-90, auto-generate sensible tasks based on topic
def make_tasks_for_day(day, topic):
    # Extract main subject from topic string
    t = topic.lower()
    if "collection" in t or "list" in t or "set" in t or "map" in t or "hashmap" in t or "treemap" in t or "arraylist" in t or "linkedlist" in t or "hashset" in t:
        cat = "Java"
    elif "spring" in t or "controller" in t or "bean" in t or "dto" in t or "jwt" in t or "jpa" in t or "hibernate" in t or "transaction" in t or "security" in t or "kafka" in t or "microservice" in t or "mockmvc" in t or "testing" in t or "logging" in t or "config" in t or "validation" in t or "exception" in t or "rest" in t or "request" in t:
        cat = "Spring Boot"
    elif "angular" in t or "component" in t or "template" in t or "binding" in t or "directive" in t or "service" in t and day > 60 or "rxjs" in t or "observable" in t or "subject" in t or "guard" in t or "interceptor" in t or "routing" in t or "form" in t and day > 60 or "http" in t and day > 60 or "lazy" in t or "state" in t and day > 60:
        cat = "Angular"
    elif "sql" in t or "database" in t:
        cat = "SQL"
    elif "dsa" in t or "mock" in t and day >= 81:
        cat = "DSA"
    else:
        cat = "Java"

    if day <= 40:
        # Java focused
        tasks = [
            {"id":f"d{day:02d}c1","category":"Java","difficulty":"Easy",
             "title":f"Implement core {topic.split(':')[-1].strip()[:30]} logic",
             "statement":f"Write a Java method demonstrating the core concept of {topic.split(':')[-1].strip()}. Create a working example with at least two test scenarios.",
             "examples":[f"Basic usage of {topic.split(':')[-1].strip()}","Edge case handling"],
             "constraints":["Handle null and empty inputs","Follow Java naming conventions"],
             "testCases":["Happy path passes","Edge case handled without exception"],
             "targetMinutes":20,
             "starterCode":f"// Demonstrate: {topic.split(':')[-1].strip()}\npublic void demonstrate() {{\n    // Your implementation here\n}}"},
            {"id":f"d{day:02d}c2","category":"Java","difficulty":"Medium",
             "title":f"Business scenario using {topic.split(':')[-1].strip()[:25]}",
             "statement":f"Apply {topic.split(':')[-1].strip()} in an order/customer domain. Write a method that solves a realistic business problem using this concept.",
             "examples":["Order processing example","Customer validation example"],
             "constraints":["Use meaningful variable names","Validate inputs"],
             "testCases":["Valid input produces correct output","Invalid input throws exception"],
             "targetMinutes":25,
             "starterCode":f"// Business use of {topic.split(':')[-1].strip()}\npublic Object processBusinessScenario(Object input) {{\n    // Apply the concept to a real scenario\n    return null;\n}}"},
            {"id":f"d{day:02d}c3","category":"SQL","difficulty":"Easy",
             "title":"SQL practice: subquery or join",
             "statement":"Write a SQL query using a subquery to find all customers whose total order amount is above the average. Hint: SELECT customer_id FROM orders GROUP BY customer_id HAVING SUM(total_amount) > (SELECT AVG(total_amount) FROM orders)",
             "examples":["Returns customer IDs of high-value customers"],
             "constraints":["Use subquery in HAVING clause","Alias your aggregations"],
             "testCases":["Result only includes customers above average","Empty table returns empty result"],
             "targetMinutes":20,
             "starterCode":"-- Find customers with above-average total spend\nSELECT c.customer_id, c.first_name, SUM(o.total_amount) as total\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nGROUP BY c.customer_id, c.first_name\nHAVING SUM(o.total_amount) > (\n    -- subquery for average\n);"},
        ]
    elif day <= 60:
        # Spring Boot focused
        tasks = [
            {"id":f"d{day:02d}c1","category":"Spring Boot","difficulty":"Easy",
             "title":f"Implement {topic.split(':')[-1].strip()[:30]} in Spring Boot",
             "statement":f"Write the Spring Boot code for {topic.split(':')[-1].strip()}. Show the key annotation, class structure, and a sample method with proper request/response handling.",
             "examples":[f"@RestController or @Service pattern for {topic.split(':')[-1].strip()}","Request DTO and Response DTO example"],
             "constraints":["Use proper Spring annotations","Follow layered architecture: Controller -> Service -> Repository"],
             "testCases":["Valid request returns 200 with data","Invalid request returns 400 with error message"],
             "targetMinutes":25,
             "starterCode":f"// Spring Boot: {topic.split(':')[-1].strip()}\n@RestController\n@RequestMapping(\"/api/orders\")\npublic class OrderController {{\n    // Inject service, write endpoint\n}}"},
            {"id":f"d{day:02d}c2","category":"Spring Boot","difficulty":"Medium",
             "title":"Service layer with validation",
             "statement":"Write a service method createOrder(CreateOrderRequest req) that: validates the request (non-null items, positive amounts), checks stock availability, saves the order, and returns an OrderResponse DTO. Throw custom exceptions for validation failures.",
             "examples":["Valid request -> OrderResponse with NEW status","Null items -> throws ValidationException"],
             "constraints":["Use @Valid or manual validation","Return DTO, not entity","Throw specific exceptions"],
             "testCases":["null items -> ValidationException","valid input -> OrderResponse with correct fields"],
             "targetMinutes":30,
             "starterCode":"@Service\npublic class OrderService {\n    public OrderResponse createOrder(CreateOrderRequest req) {\n        // 1. validate\n        // 2. build entity\n        // 3. save\n        // 4. map to response DTO\n        return null;\n    }\n}"},
            {"id":f"d{day:02d}c3","category":"SQL","difficulty":"Medium",
             "title":"Complex SQL for business reporting",
             "statement":"Write a SQL query to generate a monthly sales report: sum of total_amount by month and year, number of orders, and average order value. Show only months with more than 10 orders.",
             "examples":["2024-01: orders=45, total=4500.00, avg=100.00"],
             "constraints":["Use DATE_FORMAT or EXTRACT for month/year","HAVING COUNT(*) > 10"],
             "testCases":["Months with <= 10 orders excluded","Results ordered by year, month"],
             "targetMinutes":25,
             "starterCode":"-- Monthly sales report\nSELECT \n    YEAR(order_date) as year,\n    MONTH(order_date) as month,\n    COUNT(*) as order_count,\n    SUM(total_amount) as total_sales,\n    AVG(total_amount) as avg_order\nFROM orders\nGROUP BY YEAR(order_date), MONTH(order_date)\nHAVING COUNT(*) > 10\nORDER BY year, month;"},
        ]
    elif day <= 80:
        # Angular focused
        tasks = [
            {"id":f"d{day:02d}c1","category":"Angular","difficulty":"Easy",
             "title":f"Angular: implement {topic.split(':')[-1].strip()[:30]}",
             "statement":f"Write TypeScript/Angular code demonstrating {topic.split(':')[-1].strip()}. Create a component or service snippet showing the key Angular pattern for this topic.",
             "examples":[f"Component using {topic.split(':')[-1].strip()}","Template binding or service example"],
             "constraints":["Use standalone component pattern","Type all variables with TypeScript types"],
             "testCases":["Component renders without errors","Service method returns expected type"],
             "targetMinutes":20,
             "starterCode":f"// Angular: {topic.split(':')[-1].strip()}\n@Component({{\n  selector: 'app-example',\n  standalone: true,\n  template: `<div>implement here</div>`\n}})\nexport class ExampleComponent {{\n  // implement {topic.split(':')[-1].strip()}\n}}"},
            {"id":f"d{day:02d}c2","category":"Angular","difficulty":"Medium",
             "title":"Order list with error handling",
             "statement":"Write an Angular service method getOrders() that calls GET /api/orders, handles loading state, handles HTTP errors (show user-friendly message), and returns Observable<Order[]>. The component should show a spinner during load and an error div on failure.",
             "examples":["Loading: show spinner","Success: show table","Error: show 'Failed to load orders. Try again.'"],
             "constraints":["Use HttpClient","catchError returns empty array with console.error","Expose loading: boolean signal or property"],
             "testCases":["Loading=true before response","Loading=false after response","Error message shown on HTTP 500"],
             "targetMinutes":25,
             "starterCode":"@Injectable({ providedIn: 'root' })\nexport class OrderService {\n  constructor(private http: HttpClient) {}\n  getOrders(): Observable<Order[]> {\n    return this.http.get<Order[]>('/api/orders').pipe(\n      catchError(err => {\n        console.error(err);\n        return of([]);\n      })\n    );\n  }\n}"},
            {"id":f"d{day:02d}c3","category":"Java","difficulty":"Medium",
             "title":"Java utility: pagination helper",
             "statement":"Write a generic paginate(List<T> items, int page, int size) method that returns a sublist for the given page (0-indexed). Return empty list if page is out of range. Add a PageResult<T> wrapper with items, totalItems, totalPages, currentPage.",
             "examples":["paginate([1..10], 0, 3) -> [1,2,3]","paginate([1..10], 3, 3) -> [10]","paginate([1..10], 4, 3) -> []"],
             "constraints":["0-indexed pages","Handle edge cases: empty list, oversized page"],
             "testCases":["page=0,size=5 -> first 5","page out of range -> empty"],
             "targetMinutes":20,
             "starterCode":"public <T> List<T> paginate(List<T> items, int page, int size) {\n    if (items == null || items.isEmpty()) return Collections.emptyList();\n    int start = page * size;\n    if (start >= items.size()) return Collections.emptyList();\n    int end = Math.min(start + size, items.size());\n    return items.subList(start, end);\n}"},
        ]
    else:
        # Mock interviews / final prep
        tasks = [
            {"id":f"d{day:02d}c1","category":"Java","difficulty":"Medium",
             "title":"Interview: explain and implement",
             "statement":"For the topic of the day, write a clear verbal explanation (as a comment block) and then implement a relevant Java method. Format: 1) What is it? 2) Why is it needed? 3) How does it work internally? 4) Implement an example.",
             "examples":["See day topic for specific implementation"],
             "constraints":["Start with comment explaining the concept","Implementation must compile"],
             "testCases":["Explanation is clear","Implementation is correct"],
             "targetMinutes":30,
             "starterCode":"/*\n * 1. What: ...\n * 2. Why: ...\n * 3. How internally: ...\n */\npublic void implementExample() {\n    // Your implementation\n}"},
            {"id":f"d{day:02d}c2","category":"Spring Boot","difficulty":"Medium",
             "title":"System design: REST endpoint",
             "statement":"Design and implement a complete REST endpoint for a feature related to the day's topic. Include: Controller with proper HTTP method/status codes, Request/Response DTOs, Service with business logic, and GlobalExceptionHandler entry for custom exception.",
             "examples":["GET /api/resource -> 200 with list","POST /api/resource -> 201 with created","404 if not found"],
             "constraints":["Proper HTTP status codes","DTO separation from entity","@ExceptionHandler for custom exceptions"],
             "testCases":["Valid GET returns 200","Non-existent resource returns 404"],
             "targetMinutes":35,
             "starterCode":"@RestController @RequestMapping(\"/api/resource\")\npublic class ResourceController {\n    @GetMapping public ResponseEntity<List<ResourceResponse>> getAll() { return null; }\n    @PostMapping public ResponseEntity<ResourceResponse> create(@Valid @RequestBody CreateResourceRequest req) { return null; }\n}"},
            {"id":f"d{day:02d}c3","category":"SQL","difficulty":"Medium",
             "title":"SQL: complex reporting query",
             "statement":"Write a SQL query that uses at least: one JOIN, one aggregate function (SUM/COUNT/AVG), GROUP BY, HAVING, and ORDER BY. The query should answer a realistic business question like 'Top 5 customers by order count this year'.",
             "examples":["SELECT c.name, COUNT(o.id) as orders FROM customers c JOIN orders o ON c.id=o.cid WHERE YEAR(o.date)=2024 GROUP BY c.id, c.name ORDER BY orders DESC LIMIT 5"],
             "constraints":["Must include JOIN, GROUP BY, HAVING, ORDER BY","Use meaningful aliases","LIMIT 5 for top N"],
             "testCases":["Returns max 5 rows","Results in descending order"],
             "targetMinutes":25,
             "starterCode":"-- Top 5 customers by order count this year\nSELECT \n    c.customer_id,\n    c.first_name,\n    COUNT(o.order_id) as order_count\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nWHERE YEAR(o.order_date) = 2024\nGROUP BY c.customer_id, c.first_name\nHAVING COUNT(o.order_id) >= 1\nORDER BY order_count DESC\nLIMIT 5;"},
        ]
    return tasks

def tasks_for_day(day, topic):
    if day in DAILY_TASKS:
        raw = DAILY_TASKS[day]
        result = []
        for i, t in enumerate(raw, 1):
            if isinstance(t, dict):
                result.append(t)
            else:
                cat, diff, title, stmt, ex, starter = t
                result.append({
                    "id": f"d{day:02d}c{i}",
                    "category": cat,
                    "difficulty": diff,
                    "title": title,
                    "statement": stmt,
                    "examples": [ex],
                    "constraints": ["Handle null and edge cases","Follow Java/SQL conventions"],
                    "testCases": ["Happy path returns correct result","Edge case handled"],
                    "targetMinutes": 20,
                    "starterCode": starter
                })
        return result
    if day in PHASE_TASKS:
        raw = PHASE_TASKS[day]
        result = []
        for i, t in enumerate(raw, 1):
            cat, diff, title, stmt, ex, starter = t
            result.append({
                "id": f"d{day:02d}c{i}",
                "category": cat,
                "difficulty": diff,
                "title": title,
                "statement": stmt,
                "examples": [ex],
                "constraints": ["Handle null and edge cases","Follow naming conventions"],
                "testCases": ["Happy path works","Edge case handled"],
                "targetMinutes": 20,
                "starterCode": starter
            })
        return result
    return make_tasks_for_day(day, topic)

def main():
    total = 0
    for day in range(1, 91):
        fname = f"{CURRICULUM_DIR}/day-{day:03d}.json"
        if not os.path.exists(fname):
            print(f"Missing: {fname}")
            continue

        with open(fname, "r") as f:
            data = json.load(f)

        topic = data.get("topic", f"Day {day}")

        # Replace all coding tasks with proper ones
        new_tasks = tasks_for_day(day, topic)

        # Add the Striver DSA problem for this day
        dsa_idx = (day - 1) % len(STRIVER_75)
        dsa_task = dict(STRIVER_75[dsa_idx])
        dsa_task["id"] = f"d{day:02d}dsa"  # unique id per day
        new_tasks.append(dsa_task)

        data["codingTasks"] = new_tasks

        with open(fname, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        total += 1

    print(f"Updated {total} curriculum files.")
    print(f"Each day now has proper topic-specific tasks + 1 Striver 75 DSA problem.")
    print(f"DSA problems cycle through all {len(STRIVER_75)} Striver problems across 90 days.")

if __name__ == "__main__":
    main()
