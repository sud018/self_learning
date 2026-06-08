package com.interviewprep.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class FileStore {
  private final Path dataDir;
  private final ObjectMapper mapper;

  public FileStore(@Value("${app.data-dir}") String dataDir) throws IOException {
    this.dataDir = Path.of(dataDir);
    Files.createDirectories(this.dataDir);
    this.mapper = new ObjectMapper().registerModule(new JavaTimeModule()).findAndRegisterModules();
  }

  public synchronized <T> List<T> readList(String fileName, TypeReference<List<T>> type) {
    Path file = dataDir.resolve(fileName);
    if (!Files.exists(file)) {
      return List.of();
    }
    try {
      return mapper.readValue(file.toFile(), type);
    } catch (IOException error) {
      throw new IllegalStateException("Could not read " + fileName, error);
    }
  }

  public synchronized <T> void writeList(String fileName, List<T> values) {
    Path file = dataDir.resolve(fileName);
    try {
      mapper.writeValue(file.toFile(), values);
    } catch (IOException error) {
      throw new IllegalStateException("Could not write " + fileName, error);
    }
  }
}
