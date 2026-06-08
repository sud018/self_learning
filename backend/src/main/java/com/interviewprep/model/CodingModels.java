package com.interviewprep.model;

import java.util.List;

public class CodingModels {
  public record CodingProblem(String id, String title, String statement, List<TestCase> testCases, String starterCode) {}
  public record TestCase(String input, String expectedOutput) {}
  public record RunCodeRequest(String email, String problemId, String code) {}
  public record RunCodeResponse(boolean passed, List<TestResult> results, String message) {}
  public record TestResult(String input, String expectedOutput, String userOutput, boolean passed) {}
  public record CodingProgressResponse(List<String> solvedProblemIds) {}
  public record MarkSolvedRequest(String email, String problemId) {}
}
