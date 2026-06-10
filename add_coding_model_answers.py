"""
Add modelAnswer and approach fields to every codingTask in all curriculum JSON files.
Model answers are generated based on the task id, title, statement, and starterCode.
"""
import json
import os
import re

DATA_DIR = "backend/data/curriculum"

JAVA_APPROACH = [
    "Read input/output types from the method signature before writing a single line",
    "Walk through the example by hand — trace each step manually",
    "Write the simplest correct solution first (brute force is fine to start)",
    "Handle edge cases: empty array/string, null, zero, negative numbers, single element",
    "Verify your return type matches the signature (int vs long vs String vs int[])",
    "Run through the test cases mentally before submitting",
]

DSA_APPROACH = [
    "State the problem clearly: what is the input, what is the output?",
    "Brute force first — even O(n²) is fine as a starting point",
    "Ask: what data structure reduces the work? HashMap for O(1) lookup, Set to track seen values",
    "Handle edge cases: empty array, single element, all same values, negative numbers",
    "Trace through one example step by step with your chosen algorithm",
    "State time complexity (O(n), O(n log n)) and space complexity (O(1), O(n))",
]

# Manually crafted model answers for known task IDs
TASK_MODEL_ANSWERS = {
    # Day 1
    "d01c1": {
        "answer": """public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        System.out.println("Java version: " + System.getProperty("java.version"));
        // What JVM does with your .java file:
        // 1. javac compiles Main.java → Main.class (bytecode)
        // 2. JVM loads Main.class via the ClassLoader
        // 3. JVM verifies the bytecode (security check)
        // 4. JIT compiler converts hot bytecode paths to machine code
        // 5. main() is called and executes
    }
}""",
        "approach": JAVA_APPROACH
    },
    "d01c2": {
        "answer": """public void showJvmMemory() {
    int stackVar = 42;             // STACK: local variables, method frames
    String poolStr = "hello";      // STRING POOL: string literals are interned
    Object heapObj = new Object(); // HEAP: all new objects live here

    System.out.println("stack=" + stackVar);
    System.out.println("pool=" + poolStr);
    System.out.println("heap=" + heapObj);
    // Output: heap=java.lang.Object@<hashcode>

    // Key insight:
    // Stack: fast, limited, auto-cleaned when method returns
    // Heap: large, managed by GC, all objects go here
    // String pool: saves memory by reusing identical literals
}""",
        "approach": JAVA_APPROACH
    },
    "d01c3": {
        "answer": """public int calculate(int a, int b, String op) {
    // Use a switch expression (Java 14+ style) — clean and readable
    return switch (op) {
        case "+" -> a + b;
        case "-" -> a - b;
        case "*" -> a * b;
        case "/" -> {
            if (b == 0) yield Integer.MIN_VALUE; // edge case: division by zero
            yield a / b;
        }
        default -> throw new IllegalArgumentException("Unknown operator: " + op);
    };
}

// Alternative (traditional switch for older Java):
// switch (op) {
//   case "+": return a + b;
//   case "-": return a - b;
//   case "*": return a * b;
//   case "/": return b == 0 ? Integer.MIN_VALUE : a / b;
// }""",
        "approach": JAVA_APPROACH
    },
    "d01dsa": {
        "answer": """public int[] twoSum(int[] nums, int target) {
    // APPROACH: HashMap stores value → index for O(1) lookup
    // For each number, check if (target - num) was already seen
    // Time: O(n)  Space: O(n)

    Map<Integer, Integer> seen = new HashMap<>();  // value -> index

    for (int i = 0; i < nums.length; i++) {
        int complement = target - nums[i];         // what we need
        if (seen.containsKey(complement)) {
            return new int[]{ seen.get(complement), i };
        }
        seen.put(nums[i], i);                      // store AFTER check (no self-use)
    }

    return new int[]{};  // problem guarantees exactly one answer, so never reached

    // WHY HashMap and not brute force?
    // Brute force: two nested loops, O(n²) — too slow for 10^4 elements
    // HashMap: one pass, O(n) — fast enough for any constraint
}""",
        "approach": DSA_APPROACH
    },
}

def build_model_answer_for_task(task: dict) -> dict:
    tid = task.get("id", "")
    title = task.get("title", "").lower()
    statement = task.get("statement", "").lower()
    starter = task.get("starterCode", "")
    category = task.get("category", "Java")

    # Use hand-crafted answer if available
    if tid in TASK_MODEL_ANSWERS:
        entry = TASK_MODEL_ANSWERS[tid]
        task["modelAnswer"] = entry["answer"]
        task["approach"] = entry.get("approach", JAVA_APPROACH)
        return task

    # Generate approach based on category
    approach = DSA_APPROACH if category == "DSA" else JAVA_APPROACH

    # Generate model answer heuristically based on patterns in starter code
    answer = generate_from_starter(task, starter, title, statement, category)

    task["modelAnswer"] = answer
    task["approach"] = approach
    return task


def generate_from_starter(task: dict, starter: str, title: str, statement: str, category: str) -> str:
    """Generate a model answer based on the method signature in the starter code."""
    # Extract method signature
    sig_match = re.search(r'public\s+(\S+)\s+(\w+)\(([^)]*)\)', starter)
    if not sig_match:
        return generate_generic_hint(title, statement, category)

    return_type = sig_match.group(1)
    method_name = sig_match.group(2)
    params = sig_match.group(3).strip()

    lines = [starter.strip()]

    # Add comment-based explanation of the approach
    lines.append("")
    lines.append("// ─── HOW TO THINK ABOUT THIS ───")

    if category == "DSA":
        lines.append("// 1. Identify input/output from the signature")
        lines.append("// 2. Brute force: iterate and check/accumulate")
        lines.append("// 3. Optimise if needed: HashMap for O(1) lookup, sorting for ordered data")
    else:
        lines.append("// 1. Read the return type — that's your target")
        lines.append("// 2. Think about edge cases: null, empty, zero, out-of-range")
        lines.append("// 3. Write the happy path first, then add edge-case guards")

    # Generate body hints based on common patterns
    if "sort" in title or "sort" in statement:
        lines.append("""
// Model implementation:
// Arrays.sort(arr);         // O(n log n) — modifies in place
// Collections.sort(list);   // for ArrayList
// Arrays.sort(arr, (a,b) -> b - a);  // reverse order comparator""")

    elif "reverse" in title or "reverse" in statement:
        lines.append("""
// Model implementation (two-pointer):
// int left = 0, right = arr.length - 1;
// while (left < right) {
//     int tmp = arr[left];
//     arr[left] = arr[right];
//     arr[right] = tmp;
//     left++;
//     right--;
// }""")

    elif "palindrome" in title or "palindrome" in statement:
        lines.append("""
// Model implementation:
// String clean = s.toLowerCase().replaceAll("[^a-z0-9]", "");
// int l = 0, r = clean.length() - 1;
// while (l < r) {
//     if (clean.charAt(l) != clean.charAt(r)) return false;
//     l++; r--;
// }
// return true;""")

    elif "fibonacci" in title or "fibonacci" in statement:
        lines.append("""
// Model implementation (iterative — O(n) time, O(1) space):
// if (n <= 1) return n;
// int prev = 0, curr = 1;
// for (int i = 2; i <= n; i++) {
//     int next = prev + curr;
//     prev = curr;
//     curr = next;
// }
// return curr;""")

    elif "factorial" in title or "factorial" in statement:
        lines.append("""
// Model implementation:
// long result = 1;
// for (int i = 2; i <= n; i++) result *= i;
// return result;
// Note: use long for n > 12 (int overflows at 13!)""")

    elif "prime" in title or "prime" in statement:
        lines.append("""
// Model implementation:
// if (n < 2) return false;
// if (n == 2) return true;
// if (n % 2 == 0) return false;
// for (int i = 3; i * i <= n; i += 2) {  // only check up to sqrt(n)
//     if (n % i == 0) return false;
// }
// return true;""")

    elif "convert" in title and "salary" in title:
        lines.append("""
// Model implementation:
// String s = String.valueOf((int) salary);  // double -> int -> String
// return Integer.parseInt(s);               // String -> int""")

    elif "celsius" in title or "fahrenheit" in title or "convert" in title:
        lines.append("""
// Model implementation:
// return (celsius * 9.0 / 5.0) + 32;
// Note: use 9.0 not 9 to avoid integer division!""")

    elif "swap" in title or "swap" in statement:
        lines.append("""
// Model implementation (in-place, no temp variable):
// arr[i] ^= arr[j];
// arr[j] ^= arr[i];
// arr[i] ^= arr[j];
//
// OR readable version with temp:
// int tmp = arr[i];
// arr[i] = arr[j];
// arr[j] = tmp;""")

    elif "sum" in title or "sum" in statement:
        lines.append("""
// Model implementation:
// int sum = 0;
// for (int num : nums) sum += num;
// return sum;
// Edge case: empty array → returns 0 (correct — sum of nothing is 0)""")

    elif "max" in title or "maximum" in title:
        lines.append("""
// Model implementation:
// if (nums.length == 0) return Integer.MIN_VALUE;
// int max = nums[0];
// for (int i = 1; i < nums.length; i++) {
//     if (nums[i] > max) max = nums[i];
// }
// return max;""")

    elif "min" in title or "minimum" in title:
        lines.append("""
// Model implementation:
// if (nums.length == 0) return Integer.MAX_VALUE;
// int min = nums[0];
// for (int i = 1; i < nums.length; i++) {
//     if (nums[i] < min) min = nums[i];
// }
// return min;""")

    elif "count" in title or "count" in statement:
        lines.append("""
// Model implementation:
// int count = 0;
// for (int num : nums) {
//     if (num == target) count++;
// }
// return count;""")

    elif "average" in title or "average" in statement:
        lines.append("""
// Model implementation:
// if (nums.length == 0) return 0.0;
// double sum = 0;
// for (int num : nums) sum += num;
// return sum / nums.length;""")

    elif "two sum" in title or "twosum" in title:
        lines.append("""
// Model implementation (HashMap, O(n)):
// Map<Integer, Integer> seen = new HashMap<>();
// for (int i = 0; i < nums.length; i++) {
//     int complement = target - nums[i];
//     if (seen.containsKey(complement)) {
//         return new int[]{ seen.get(complement), i };
//     }
//     seen.put(nums[i], i);
// }
// return new int[]{};""")

    elif return_type == "boolean" or return_type == "bool":
        lines.append("""
// Pattern for boolean methods:
// - Start with the false / guard conditions
// - if (condition_that_makes_it_false) return false;
// - All other paths return true""")

    elif "[]" in return_type:
        lines.append(f"""
// Pattern for array-returning methods:
// int[] result = new int[expectedSize];
// // fill result array
// return result;""")

    else:
        lines.append("""
// General pattern:
// 1. Handle edge/null cases at the top
// 2. Write the main logic
// 3. Return the correct type""")

    # Add complexity note
    lines.append("")
    lines.append(f"// Time complexity: O(n) typical for single-pass problems")
    lines.append(f"// Space complexity: O(1) if in-place, O(n) if extra storage needed")

    return "\n".join(lines)


def generate_generic_hint(title: str, statement: str, category: str) -> str:
    return f"""// ─── HOW TO SOLVE: {title} ───
//
// Step 1: Read the return type carefully — that is your goal
// Step 2: Walk through the example manually before writing code
// Step 3: Handle edge cases first (empty, null, zero, single element)
// Step 4: Write the simplest correct logic — don't over-engineer
// Step 5: Test against each provided test case
//
// Hint from statement: {statement[:200]}
//
// Time complexity goal: O(n) single pass
// Space complexity goal: O(1) if modifying in place
"""


def process_file(filepath: str) -> None:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    tasks = data.get("codingTasks", [])
    changed = False
    for task in tasks:
        if "modelAnswer" not in task or not task.get("modelAnswer"):
            build_model_answer_for_task(task)
            changed = True

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  Updated: {os.path.basename(filepath)}")
    else:
        print(f"  Skipped (already has answers): {os.path.basename(filepath)}")


def main():
    files = sorted([
        os.path.join(DATA_DIR, f)
        for f in os.listdir(DATA_DIR)
        if f.endswith(".json")
    ])
    print(f"Processing {len(files)} curriculum files...")
    for fp in files:
        process_file(fp)
    print("Done.")


if __name__ == "__main__":
    main()
