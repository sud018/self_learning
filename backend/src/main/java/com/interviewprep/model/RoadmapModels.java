package com.interviewprep.model;

import java.util.List;

public class RoadmapModels {
  public record RoadmapModule(String name, List<String> topics) {}
}
