package com.interviewprep.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class SpaController {
  @GetMapping({"/", "/dashboard", "/daily-assignment", "/roadmap", "/coding", "/missed-day"})
  public String app() {
    return "forward:/index.html";
  }
}
