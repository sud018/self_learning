package com.interviewprep.controller;

import com.interviewprep.model.CodingModels.CodingProblem;
import com.interviewprep.model.CodingModels.CodingProgressResponse;
import com.interviewprep.model.CodingModels.MarkSolvedRequest;
import com.interviewprep.model.CodingModels.RunCodeRequest;
import com.interviewprep.model.CodingModels.RunCodeResponse;
import com.interviewprep.service.CodingService;
import com.interviewprep.service.ProgressService;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/coding")
public class CodingController {
  private final CodingService codingService;
  private final ProgressService progressService;

  public CodingController(CodingService codingService, ProgressService progressService) {
    this.codingService = codingService;
    this.progressService = progressService;
  }

  @GetMapping("/problems")
  List<CodingProblem> problems() {
    return codingService.problems();
  }

  @GetMapping("/progress")
  CodingProgressResponse progress(@RequestParam String email) {
    return new CodingProgressResponse(progressService.solvedCodingProblemIds(email));
  }

  @PostMapping("/mark-solved")
  CodingProgressResponse markSolved(@RequestBody MarkSolvedRequest request) {
    progressService.markCodingProblemSolved(request.email(), request.problemId());
    return new CodingProgressResponse(progressService.solvedCodingProblemIds(request.email()));
  }

  @PostMapping("/run")
  RunCodeResponse run(@RequestBody RunCodeRequest request) {
    return codingService.run(request.problemId(), request.code());
  }

  @PostMapping("/submit")
  RunCodeResponse submit(@RequestBody RunCodeRequest request) {
    RunCodeResponse response = codingService.submit(request.problemId(), request.code());
    String pointSource = "Coding problem solved: " + request.problemId();
    if (response.passed()) {
      boolean newlySolved = progressService.markCodingProblemSolved(request.email(), request.problemId());
      if (newlySolved && !progressService.hasPointEvent(request.email(), pointSource)) {
        progressService.addPoints(request.email(), pointSource, 30);
      }
    }
    return response;
  }
}
