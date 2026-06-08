package com.interviewprep.controller;

import com.interviewprep.model.Dashboard;
import com.interviewprep.service.ProgressService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {
  private final ProgressService progressService;

  public DashboardController(ProgressService progressService) {
    this.progressService = progressService;
  }

  @GetMapping
  Dashboard dashboard(@RequestParam String email) {
    return progressService.dashboard(email);
  }
}
