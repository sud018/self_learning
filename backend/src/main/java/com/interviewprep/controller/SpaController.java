package com.interviewprep.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class SpaController {
  // Catch all GET requests that are not API calls or static files, and serve index.html
  // Angular's router handles the actual routing on the client side.
  @GetMapping({
      "/", "/dashboard", "/daily-assignment", "/roadmap", "/coding", "/missed-day", "/tracker", "/daily",
      "/dashboard/**", "/daily-assignment/**", "/roadmap/**", "/coding/**", "/missed-day/**", "/tracker/**", "/daily/**"
  })
  public String app() {
    return "forward:/index.html";
  }
}
