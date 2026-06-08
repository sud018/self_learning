package com.interviewprep.service;

import jakarta.annotation.PostConstruct;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class DataInitializer {
  private final Path dataDir;
  private final Path seedDataDir;

  public DataInitializer(@Value("${app.data-dir}") String dataDir, @Value("${app.seed-data-dir}") String seedDataDir) {
    this.dataDir = Path.of(dataDir);
    this.seedDataDir = Path.of(seedDataDir);
  }

  @PostConstruct
  public void initialize() throws IOException {
    Files.createDirectories(dataDir);
    copyDirectoryIfMissing("curriculum");
    copyFileIfMissing("daily-notes.txt");
    copyFileIfMissing("attempts.txt");
    copyFileIfMissing("coding-progress.txt");
    copyFileIfMissing("progress.txt");
  }

  private void copyDirectoryIfMissing(String name) throws IOException {
    Path source = seedDataDir.resolve(name);
    Path target = dataDir.resolve(name);
    if (!Files.exists(source) || Files.exists(target)) {
      return;
    }
    try (var paths = Files.walk(source)) {
      for (Path path : paths.toList()) {
        Path destination = target.resolve(source.relativize(path));
        if (Files.isDirectory(path)) {
          Files.createDirectories(destination);
        } else {
          Files.copy(path, destination, StandardCopyOption.REPLACE_EXISTING);
        }
      }
    }
  }

  private void copyFileIfMissing(String name) throws IOException {
    Path source = seedDataDir.resolve(name);
    Path target = dataDir.resolve(name);
    if (Files.exists(source) && !Files.exists(target)) {
      Files.createDirectories(target.getParent());
      Files.copy(source, target, StandardCopyOption.REPLACE_EXISTING);
    }
  }
}
