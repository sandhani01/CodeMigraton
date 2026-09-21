package com.example.CodeMigraton.controller;

import com.example.CodeMigraton.dto.ProjectCreateRequest;
import com.example.CodeMigraton.dto.ProjectResponse;
import com.example.CodeMigraton.service.ProjectService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
public class ProjectController {

    private final ProjectService projectService;

    public ProjectController(ProjectService projectService) {
        this.projectService = projectService;
    }

    @GetMapping("/api/projects/{id}")
    public ResponseEntity<ProjectResponse> findProjectById(
            @PathVariable Long id) {

        return ResponseEntity.ok(
                projectService.findProjectById(id)
        );
    }

    @GetMapping("/api/projects")
    public ResponseEntity<List<ProjectResponse>> giveAllProjects() {

        return ResponseEntity.ok(
                projectService.giveAllProjects()
        );
    }

    @GetMapping("/api/app-details")
    public String getAppDetails() {
        return projectService.getAppDetails();
    }

    @PostMapping("/api/projects")
    public ResponseEntity<ProjectResponse> createProject(
            @Valid @RequestBody ProjectCreateRequest request) {

        ProjectResponse response =
                projectService.createProject(request);

        return ResponseEntity.status(201).body(response);
    }

    @DeleteMapping("/api/projects/{id}")
    public ResponseEntity<Void> deleteProject(
            @PathVariable Long id) {

        projectService.deleteProject(id);

        return ResponseEntity.noContent().build();
    }

    @PutMapping("/api/projects/{id}")
    public ResponseEntity<ProjectResponse> updateProject(
            @PathVariable Long id,
            @Valid @RequestBody ProjectCreateRequest request) {

        ProjectResponse response =
                projectService.updateProject(id, request);

        return ResponseEntity.ok(response);
    }
}