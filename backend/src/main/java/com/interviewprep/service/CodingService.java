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

  private String methodName(Assignment.CodingTask task) {
    Matcher matcher = Pattern.compile("public\\s+\\w+\\s+(\\w+)\\s*\\(").matcher(task.starterCode());
    if (matcher.find()) {
      return matcher.group(1);
    }
    throw new IllegalArgumentException("Could not detect Java method name for " + task.id());
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

    Path workDir = null;
    try {
      workDir = Files.createTempDirectory("interview-prep-code-");
      Files.writeString(workDir.resolve("Solution.java"), solutionSource(code), StandardCharsets.UTF_8);
      Files.writeString(workDir.resolve("Runner.java"), runnerSource(problem, tests), StandardCharsets.UTF_8);

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
        String[] withoutTrailingLine = new String[outputs.length - 1];
        System.arraycopy(outputs, 0, withoutTrailingLine, 0, withoutTrailingLine.length);
        outputs = withoutTrailingLine;
      }
      List<TestResult> results = new ArrayList<>();
      for (int index = 0; index < tests.size(); index++) {
        TestCase test = tests.get(index);
        String userOutput = index < outputs.length ? outputs[index].trim() : "";
        results.add(new TestResult(test.input(), test.expectedOutput(), userOutput, test.expectedOutput().equals(userOutput)));
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

  private String solutionSource(String code) {
    if (code.contains("class Solution")) {
      return code;
    }
    return "public class Solution {\n" + code + "\n}\n";
  }

  private String runnerSource(ProblemSpec problem, List<TestCase> tests) {
    StringBuilder calls = new StringBuilder();
    for (TestCase test : tests) {
      calls.append("    System.out.println(String.valueOf(solution.")
          .append(actualMethodName(problem))
          .append("(")
          .append(argumentLiteral(problem, test.input()))
          .append(")));\n");
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

  private String argumentLiteral(ProblemSpec problem, String input) {
    if (problem.methodName().equals("isValid") || problem.methodName().equals("solveString")) {
      if (input.equalsIgnoreCase("null")) {
        return "null";
      }
      return javaString(input);
    }
    if (problem.methodName().equals("countTarget")) {
      String[] parts = input.split("\\s*,\\s*(?![^\\[]*\\])", 2);
      String array = parts.length > 0 ? parts[0].trim() : "[]";
      String target = parts.length > 1 ? parts[1].trim() : "0";
      return intArray(array) + ", " + target;
    }
    return intArray(input);
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
