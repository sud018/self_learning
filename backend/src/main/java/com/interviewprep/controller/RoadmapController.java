package com.interviewprep.controller;

import com.interviewprep.model.RoadmapModels.RoadmapModule;
import com.interviewprep.service.RoadmapService;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/roadmap")
public class RoadmapController {
  private final RoadmapService roadmapService;

  public RoadmapController(RoadmapService roadmapService) {
    this.roadmapService = roadmapService;
  }

  @GetMapping
  List<RoadmapModule> roadmap() {
    return roadmapService.roadmap();
  }
}
