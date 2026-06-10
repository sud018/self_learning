package com.interviewprep.service;

import com.interviewprep.model.Assignment;
import com.interviewprep.model.CodingModels.CodingProblem;
import com.interviewprep.model.CodingModels.RunCodeResponse;
import com.interviewprep.model.CodingModels.TestCase;
import com.interviewprep.model.CodingModels.TestResult;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.tools.ToolProvider;
import org.springframework.stereotype.Service;

@Service
public class CodingService {
  private final AssignmentService assignmentService;

  public CodingService(AssignmentService assignmentService) {
    this.assignmentService = assignmentService;
  }

  public List<CodingProblem> problems() {
    return List.of(
        new CodingProblem("reverse-string", "Reverse a string", "Write Java logic that returns the reverse of the input string.",
            List.of(new TestCase("java", "avaj"), new TestCase("spring", "gnirps")),
            "public String solve(String input) {\n  return \"\";\n}"),
        new CodingProblem("array-sum", "Array sum", "Return the sum of numbers in an integer array.",
            List.of(new TestCase("[1,2,3]", "6"), new TestCase("[10,-2,5]", "13")),
            "public int solve(int[] nums) {\n  return 0;\n}")
    );
  }

  public RunCodeResponse run(String problemId, String code) {
    ProblemSpec problem = findProblem(problemId);
    return evaluate(problem, code, problem.sampleTests());
  }

  public RunCodeResponse submit(String problemId, String code) {
    ProblemSpec problem = findProblem(problemId);
    List<TestCase> tests = new ArrayList<>(problem.sampleTests());
    tests.addAll(edgeTests(problem));
    return evaluate(problem, code, tests);
  }

  private ProblemSpec findProblem(String problemId) {
    Optional<CodingProblem> standalone = problems().stream()
        .filter(item -> item.id().equals(problemId))
        .findFirst();
    if (standalone.isPresent()) {
      CodingProblem problem = standalone.get();
      String methodName = problem.id().equals("reverse-string") ? "solveString" : "solveIntArray";
      return new ProblemSpec(problem.id(), methodName, problem.testCases(), problem.starterCode());
    }

    return assignmentService.assignments().stream()
        .flatMap(assignment -> assignment.codingTasks().stream())
        .filter(task -> task.id().equals(problemId))
        .findFirst()
        .map(task -> new ProblemSpec(task.id(), methodName(task), parseTests(task.testCases()), task.starterCode()))
        .or(() -> assignmentService.assignments().stream()
            .flatMap(assignment -> assignment.dsaPractice().stream())
            .filter(problem -> problem.id().equals(problemId))
            .findFirst()
            .map(this::dsaProblemSpec))
        .orElseThrow(() -> new IllegalArgumentException("Unknown coding problem: " + problemId));
  }

  private ProblemSpec dsaProblemSpec(Assignment.DsaProblem problem) {
    String title = problem.title().toLowerCase(Locale.ROOT);
    if (title.contains("maximum")) {
      return new ProblemSpec(problem.id(), "maxValue", List.of(
          new TestCase("[1,5,2]", "5"),
          new TestCase("[-3,-1,-7]", "-1")
      ), "public int maxValue(int[] nums) {\n  // write Java solution\n  return 0;\n}");
    }
    if (title.contains("count target")) {
      return new ProblemSpec(problem.id(), "countTarget", List.of(
          new TestCase("[2,1,2,3], 2", "2"),
          new TestCase("[], 5", "0")
      ), "public int countTarget(int[] nums, int target) {\n  // write Java solution\n  return 0;\n}");
    }
    return new ProblemSpec(problem.id(), "solveIntArray", List.of(
        new TestCase("[1,2,3]", "6"),
        new TestCase("[]", "0")
    ), "public int solve(int[] nums) {\n  // default DSA practice: return the sum of nums\n  return 0;\n}");
  }

  private static final String PROGRAM_MODE = "__program__";

  /** Returns PROGRAM_MODE for full-class code, otherwise the callable method name. */
  private String methodName(Assignment.CodingTask task) {
    if (isProgramMode(task.starterCode())) {
      return PROGRAM_MODE;
    }
    // Match: public [static] [final] ReturnType methodName(
    Matcher m = Pattern.compile(
        "public\\s+(?:static\\s+)?(?:final\\s+)?[\\w<>\\[\\]]+\\s+(\\w+)\\s*\\(")
        .matcher(task.starterCode());
    while (m.find()) {
      String name = m.group(1);
      if (!name.matches("class|interface|enum|record|main")) return name;
    }
    throw new IllegalArgumentException(
        "Could not detect Java method name for " + task.id()
        + ". Starter code should have a method like: public int solve(int[] nums)");
  }

  private boolean isProgramMode(String code) {
    return code.contains("public class") && code.contains("main(");
  }

  private List<TestCase> parseTests(List<String> rawTests) {
    return rawTests.stream()
        .map(test -> test.split("\\s*->\\s*", 2))
        .filter(parts -> parts.length == 2)
        .map(parts -> new TestCase(parts[0].trim(), parts[1].trim()))
        .toList();
  }

  private RunCodeResponse evaluate(ProblemSpec problem, String code, List<TestCase> tests) {
    if (ToolProvider.getSystemJavaCompiler() == null) {
      return new RunCodeResponse(false, List.of(), "Java compiler is not available. Run the backend with a JDK, not a JRE.");
    }

    if (PROGRAM_MODE.equals(problem.methodName()) || isProgramMode(code)) {
      return evaluateProgramMode(code, tests);
    }

    List<String> paramTypes = extractParamTypes(problem.starterCode());
    if (!isAutoRunnable(paramTypes)) {
      return new RunCodeResponse(true, List.of(),
          "✓ Solution recorded — this problem uses custom types that cannot be auto-compiled.\nReview your logic against the examples manually.");
    }

    Path workDir = null;
    try {
      workDir = Files.createTempDirectory("interview-prep-code-");
      Files.writeString(workDir.resolve("Solution.java"), solutionSource(code), StandardCharsets.UTF_8);
      Files.writeString(workDir.resolve("Runner.java"), runnerSource(problem, paramTypes, tests), StandardCharsets.UTF_8);

      ProcessResult compile = runProcess(workDir, javaTool("javac"), "Solution.java", "Runner.java");
      if (compile.exitCode() != 0) {
        return new RunCodeResponse(false, List.of(), "Compilation failed:\n" + compile.output());
      }

      ProcessResult execution = runProcess(workDir, javaTool("java"), "Runner");
      if (execution.exitCode() != 0) {
        return new RunCodeResponse(false, List.of(), "Runtime error:\n" + execution.output());
      }

      String[] outputs = execution.output().split("\\R", -1);
      if (outputs.length > 0 && outputs[outputs.length - 1].isEmpty()) {
        String[] trimmed = new String[outputs.length - 1];
        System.arraycopy(outputs, 0, trimmed, 0, trimmed.length);
        outputs = trimmed;
      }
      List<TestResult> results = new ArrayList<>();
      for (int index = 0; index < tests.size(); index++) {
        TestCase test = tests.get(index);
        String actual = index < outputs.length ? outputs[index].trim() : "";
        // Normalize array output: strip spaces so "[2, 1]" matches "[2,1]"
        boolean passed = normalizeOutput(test.expectedOutput()).equals(normalizeOutput(actual));
        results.add(new TestResult(test.input(), test.expectedOutput(), actual, passed));
      }
      boolean passed = results.stream().allMatch(TestResult::passed);
      return new RunCodeResponse(passed, results, passed ? "All tests passed." : "Some tests failed. Review the output and fix the code.");
    } catch (InterruptedException error) {
      Thread.currentThread().interrupt();
      return new RunCodeResponse(false, List.of(), "Could not run code: " + error.getMessage());
    } catch (IOException error) {
      return new RunCodeResponse(false, List.of(), "Could not run code: " + error.getMessage());
    } finally {
      if (workDir != null) {
        deleteQuietly(workDir);
      }
    }
  }

  /** True only for types the runner can construct without custom class definitions. */
  private static final java.util.Set<String> SIMPLE_TYPES = java.util.Set.of(
      "int", "int[]", "int[][]", "double", "double[]", "float", "float[]",
      "long", "long[]", "boolean", "char", "char[]", "char[][]",
      "string", "string[]", "void"
  );

  private boolean isAutoRunnable(List<String> paramTypes) {
    return paramTypes.stream().allMatch(t -> SIMPLE_TYPES.contains(t.toLowerCase(Locale.ROOT)));
  }

  private String normalizeOutput(String s) {
    return s.trim().replaceAll("[\\s,]+", ",").replaceAll(",$", "");
  }

  /**
   * Program mode: user wrote a full public class with main().
   * Compile and run it directly; test cases use "-> expected" format
   * where the right-hand side must appear somewhere in stdout.
   */
  private RunCodeResponse evaluateProgramMode(String code, List<TestCase> tests) {
    Path workDir = null;
    try {
      workDir = Files.createTempDirectory("interview-prep-program-");

      // Extract class name from code, default to Main
      Matcher classMatcher = Pattern.compile("public\\s+class\\s+(\\w+)").matcher(code);
      String className = classMatcher.find() ? classMatcher.group(1) : "Main";

      Files.writeString(workDir.resolve(className + ".java"), code, StandardCharsets.UTF_8);

      ProcessResult compile = runProcess(workDir, javaTool("javac"), className + ".java");
      if (compile.exitCode() != 0) {
        return new RunCodeResponse(false, List.of(), "Compilation failed:\n" + compile.output());
      }

      ProcessResult execution = runProcess(workDir, javaTool("java"), className);
      if (execution.exitCode() != 0) {
        return new RunCodeResponse(false, List.of(), "Runtime error:\n" + execution.output());
      }

      String stdout = execution.output().trim();

      // If no test cases, just verify the program ran without error
      if (tests.isEmpty()) {
        return new RunCodeResponse(true, List.of(),
            "Program ran successfully.\nOutput:\n" + stdout);
      }

      // Check each test case: format "-> expected_substring"
      List<TestResult> results = new ArrayList<>();
      for (TestCase test : tests) {
        // expected is the string after "-> " (or the whole test case if no "->")
        String expected = test.expectedOutput().startsWith("->")
            ? test.expectedOutput().substring(2).trim()
            : test.expectedOutput().trim();
        boolean passed = stdout.contains(expected);
        results.add(new TestResult("(stdout check)", expected, stdout, passed));
      }

      boolean allPassed = results.stream().allMatch(TestResult::passed);
      String msg = allPassed
          ? "All checks passed.\nProgram output:\n" + stdout
          : "Some output checks failed.\nActual output:\n" + stdout;
      return new RunCodeResponse(allPassed, results, msg);

    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
      return new RunCodeResponse(false, List.of(), "Could not run program: " + e.getMessage());
    } catch (IOException e) {
      return new RunCodeResponse(false, List.of(), "Could not run program: " + e.getMessage());
    } finally {
      if (workDir != null) deleteQuietly(workDir);
    }
  }

  private String solutionSource(String code) {
    if (code.contains("class Solution")) {
      return code;
    }
    return "public class Solution {\n" + code + "\n}\n";
  }

  private String runnerSource(ProblemSpec problem, List<String> paramTypes, List<TestCase> tests) {
    String returnType = extractReturnType(problem.starterCode());
    String method = actualMethodName(problem);
    boolean voidInPlace = "void".equals(returnType) && !paramTypes.isEmpty()
        && paramTypes.get(0).endsWith("[]");
    boolean returnsArray = returnType.endsWith("[]") && !"void".equals(returnType);

    StringBuilder calls = new StringBuilder();
    int idx = 0;
    for (TestCase test : tests) {
      idx++;
      List<String> inputParts = splitInput(test.input());

      if (voidInPlace) {
        // e.g. swap(int[] arr, int i, int j) — mutates arr, no return value
        String arrType = paramTypes.get(0);           // e.g. "int[]"
        String arrLiteral = arrayLiteralForType(arrType, inputParts.isEmpty() ? "[]" : inputParts.get(0));
        String tmp = "_t" + idx;
        calls.append("    { ").append(arrType).append(" ").append(tmp).append(" = ").append(arrLiteral).append("; ");
        calls.append("solution.").append(method).append("(").append(tmp);
        for (int p = 1; p < paramTypes.size(); p++) {
          String part = p < inputParts.size() ? inputParts.get(p) : defaultForType(paramTypes.get(p));
          calls.append(", ").append(formatArgByType(paramTypes.get(p), part));
        }
        calls.append("); System.out.println(java.util.Arrays.toString(").append(tmp).append(")); }\n");
      } else if (returnsArray) {
        calls.append("    System.out.println(java.util.Arrays.toString(solution.").append(method)
            .append("(").append(buildArgList(paramTypes, inputParts)).append(")));\n");
      } else {
        calls.append("    System.out.println(String.valueOf(solution.").append(method)
            .append("(").append(buildArgList(paramTypes, inputParts)).append(")));\n");
      }
    }
    return """
        public class Runner {
          public static void main(String[] args) {
            Solution solution = new Solution();
        %s  }
        }
        """.formatted(calls);
  }

  private String actualMethodName(ProblemSpec problem) {
    return switch (problem.methodName()) {
      case "solveString" -> "solve";
      case "solveIntArray" -> "solve";
      default -> problem.methodName();
    };
  }

  // ── Argument helpers ──────────────────────────────────────────────────────

  /** Build the full argument list string from a list of param types and input parts. */
  private String buildArgList(List<String> paramTypes, List<String> inputParts) {
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < paramTypes.size(); i++) {
      if (i > 0) sb.append(", ");
      String part = i < inputParts.size() ? inputParts.get(i) : defaultForType(paramTypes.get(i));
      sb.append(formatArgByType(paramTypes.get(i), part));
    }
    return sb.toString();
  }

  /** Split "a, b, [1,2,3], c" into ["a", "b", "[1,2,3]", "c"] respecting brackets. */
  private List<String> splitInput(String input) {
    List<String> result = new ArrayList<>();
    int depth = 0;
    StringBuilder cur = new StringBuilder();
    for (char c : input.toCharArray()) {
      if (c == '[' || c == '(') depth++;
      else if (c == ']' || c == ')') depth--;
      if (c == ',' && depth == 0) {
        result.add(cur.toString().trim());
        cur.setLength(0);
      } else {
        cur.append(c);
      }
    }
    if (cur.length() > 0) result.add(cur.toString().trim());
    return result;
  }

  private String formatArgByType(String type, String input) {
    String t = type.toLowerCase(Locale.ROOT).replace(" ", "");
    return switch (t) {
      case "double"   -> input.trim();
      case "float"    -> input.trim() + "f";
      case "long"     -> input.trim() + "L";
      case "int"      -> input.trim();
      case "boolean"  -> input.trim();
      case "string"   -> {
        if (input.equalsIgnoreCase("null")) yield "null";
        yield javaString(input);
      }
      case "int[]"    -> intArray(input);
      case "int[][]"  -> int2dArray(input);
      case "char[]"   -> charArray(input);
      case "char[][]" -> char2dArray(input);
      case "double[]" -> doubleArray(input);
      default         -> inferArgument(input);
    };
  }

  private String arrayLiteralForType(String type, String input) {
    String t = type.toLowerCase(Locale.ROOT).replace(" ", "");
    return switch (t) {
      case "int[]"    -> intArray(input);
      case "char[]"   -> charArray(input);
      case "double[]" -> doubleArray(input);
      default         -> intArray(input);
    };
  }

  private String defaultForType(String type) {
    return switch (type.toLowerCase(Locale.ROOT).replace(" ", "")) {
      case "int", "long" -> "0";
      case "double", "float" -> "0.0";
      case "boolean" -> "false";
      case "string" -> "\"\"";
      default -> "null";
    };
  }

  private String inferArgument(String input) {
    String t = input.trim();
    if (t.startsWith("[")) return intArray(t);
    if (t.matches("-?\\d+\\.\\d+(?:[eE][+-]?\\d+)?")) return t;
    if (t.matches("-?\\d+")) return t;
    return intArray(t);
  }

  // ── Type extraction ───────────────────────────────────────────────────────

  private String extractReturnType(String starterCode) {
    Matcher m = Pattern.compile("public\\s+(\\S+?)\\s+\\w+\\s*\\(").matcher(starterCode);
    return m.find() ? m.group(1) : "int";
  }

  private List<String> extractParamTypes(String starterCode) {
    Matcher m = Pattern.compile("public\\s+[\\w<>\\[\\]]+\\s+\\w+\\s*\\(([^)]*)\\)").matcher(starterCode);
    if (!m.find()) return List.of();
    String params = m.group(1).trim();
    if (params.isEmpty()) return List.of();
    List<String> types = new ArrayList<>();
    for (String param : params.split(",")) {
      String[] parts = param.trim().split("\\s+");
      if (parts.length >= 2) types.add(parts[0].trim());
    }
    return types;
  }

  // ── Array literal builders ────────────────────────────────────────────────

  private String charArray(String input) {
    String value = input.replace("[", "").replace("]", "").trim();
    if (value.isEmpty()) return "new char[]{}";
    String[] items = value.split("\\s*,\\s*");
    StringBuilder sb = new StringBuilder("new char[]{");
    for (int i = 0; i < items.length; i++) {
      if (i > 0) sb.append(",");
      String ch = items[i].trim().replace("'", "");
      sb.append("'").append(ch.isEmpty() ? " " : ch.charAt(0)).append("'");
    }
    return sb.append("}").toString();
  }

  private String doubleArray(String input) {
    String value = input.replace("[", "").replace("]", "").trim();
    if (value.isEmpty()) return "new double[]{}";
    return "new double[]{" + value + "}";
  }

  private String int2dArray(String input) {
    String trimmed = input.trim();
    if (trimmed.equals("[]") || trimmed.isEmpty()) return "new int[][]{}";
    trimmed = trimmed.replaceAll("^\\[", "").replaceAll("\\]$", "").trim();
    String[] rows = trimmed.split("\\],\\s*\\[");
    StringBuilder sb = new StringBuilder("new int[][]{");
    for (int i = 0; i < rows.length; i++) {
      if (i > 0) sb.append(",");
      sb.append(intArray("[" + rows[i].replace("[", "").replace("]", "") + "]"));
    }
    return sb.append("}").toString();
  }

  private String char2dArray(String input) {
    String trimmed = input.trim();
    if (trimmed.equals("[]") || trimmed.isEmpty()) return "new char[][]{}";
    trimmed = trimmed.replaceAll("^\\[", "").replaceAll("\\]$", "").trim();
    String[] rows = trimmed.split("\\],\\s*\\[");
    StringBuilder sb = new StringBuilder("new char[][]{");
    for (int i = 0; i < rows.length; i++) {
      if (i > 0) sb.append(",");
      sb.append(charArray("[" + rows[i].replace("[", "").replace("]", "") + "]"));
    }
    return sb.append("}").toString();
  }

  private String javaString(String input) {
    String value = input;
    if (value.length() >= 2 && value.startsWith("\"") && value.endsWith("\"")) {
      value = value.substring(1, value.length() - 1);
    }
    value = value.replace("\\", "\\\\").replace("\"", "\\\"");
    return "\"" + value + "\"";
  }

  private String intArray(String input) {
    String value = input.replace("[", "").replace("]", "").trim();
    if (value.isEmpty()) {
      return "new int[]{}";
    }
    return "new int[]{" + value + "}";
  }

  private List<TestCase> edgeTests(ProblemSpec problem) {
    String key = problem.methodName().toLowerCase(Locale.ROOT);
    if (problem.id().equals("reverse-string")) {
      return List.of(
          new TestCase("\"\"", ""),
          new TestCase("\"a\"", "a"),
          new TestCase("\"racecar\"", "racecar"),
          new TestCase("\"hello world\"", "dlrow olleh")
      );
    }
    if (problem.id().equals("array-sum")) {
      return List.of(
          new TestCase("[0]", "0"),
          new TestCase("[]", "0"),
          new TestCase("[-5,5,10]", "10"),
          new TestCase("[100000,-1]", "99999")
      );
    }
    if (key.equals("isvalid")) {
      return List.of(
          new TestCase("\"\"", "false"),
          new TestCase("\"  \"", "false"),
          new TestCase("\"ab\"", "true"),
          new TestCase("\" a b \"", "true")
      );
    }
    if (key.equals("countactive")) {
      return List.of(
          new TestCase("[1,0,0,1,1]", "3"),
          new TestCase("[0]", "0"),
          new TestCase("[1,1,1,1]", "4"),
          new TestCase("[]", "0")
      );
    }
    if (key.equals("counttarget")) {
      return List.of(
          new TestCase("[1,1,1], 1", "3"),
          new TestCase("[1,2,3], 4", "0"),
          new TestCase("[5], 5", "1"),
          new TestCase("[], 0", "0")
      );
    }
    if (key.equals("maxvalue")) {
      return List.of(
          new TestCase("[0,-1,-2]", "0"),
          new TestCase("[-2147483648]", "-2147483648"),
          new TestCase("[9,9,2]", "9"),
          new TestCase("[]", String.valueOf(Integer.MIN_VALUE))
      );
    }
    if (key.equals("solveintarray")) {
      return List.of(
          new TestCase("[0]", "0"),
          new TestCase("[-1,1]", "0"),
          new TestCase("[10,20,30]", "60")
      );
    }
    return List.of();
  }

  private String javaTool(String name) {
    return Path.of(System.getProperty("java.home"), "bin", name).toString();
  }

  private ProcessResult runProcess(Path workDir, String... command) throws IOException, InterruptedException {
    Process process = new ProcessBuilder(command)
        .directory(workDir.toFile())
        .redirectErrorStream(true)
        .start();
    boolean finished = process.waitFor(Duration.ofSeconds(4).toMillis(), TimeUnit.MILLISECONDS);
    if (!finished) {
      process.destroyForcibly();
      return new ProcessResult(1, "Execution timed out after 4 seconds.");
    }
    String output = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
    return new ProcessResult(process.exitValue(), output);
  }

  private void deleteQuietly(Path path) {
    try (var paths = Files.walk(path)) {
      paths.sorted(Comparator.reverseOrder()).forEach(item -> {
        try {
          Files.deleteIfExists(item);
        } catch (IOException ignored) {
        }
      });
    } catch (IOException ignored) {
    }
  }

  private record ProblemSpec(String id, String methodName, List<TestCase> sampleTests, String starterCode) {}
  private record ProcessResult(int exitCode, String output) {}
}
