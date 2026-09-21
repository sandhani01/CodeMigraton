package com.example.CodeMigraton.service;

import com.example.CodeMigraton.config.AppProperties;
import com.example.CodeMigraton.dto.ProjectCreateRequest;
import com.example.CodeMigraton.dto.ProjectResponse;
import com.example.CodeMigraton.entity.Project;
import com.example.CodeMigraton.exception.ProjectNotFoundException;
import com.example.CodeMigraton.mapper.ProjectMapper;
import com.example.CodeMigraton.repository.ProjectRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ProjectService {

    private final ProjectRepository projectRepository;
    private final AppProperties appProperties;
    private final ProjectMapper projectMapper;

    public ProjectService(
            ProjectRepository projectRepository,
            AppProperties appProperties,
            ProjectMapper projectMapper) {

        this.projectRepository = projectRepository;
        this.appProperties = appProperties;
        this.projectMapper = projectMapper;
    }

    public String getAppDetails() {
        return "App Owner : " + appProperties.getOwner()
                + "\nApp Name : " + appProperties.getName()
                + "\nApp Version : " + appProperties.getVersion()
                + "\nEnvironment : " + appProperties.getEnvironment();
    }

    public ProjectResponse createProject(ProjectCreateRequest request) {
        Project project = new Project();
        project.setName(request.getName());

        project = projectRepository.save(project);

        return projectMapper.toResponse(project);
    }

    public ProjectResponse findProjectById(Long id) {
        Project project = projectRepository.findById(id)
                .orElseThrow(() -> new ProjectNotFoundException(id));

        return projectMapper.toResponse(project);
    }

    public void deleteProject(Long id) {
        Project project = projectRepository.findById(id)
                .orElseThrow(() -> new ProjectNotFoundException(id));

        projectRepository.delete(project);
    }

    public List<ProjectResponse> giveAllProjects() {
        List<Project> projects = projectRepository.findAll();

        return projects.stream()
                .map(projectMapper::toResponse)
                .toList();
    }

    public ProjectResponse updateProject(
            Long id,
            ProjectCreateRequest request) {

        Project project = projectRepository.findById(id)
                .orElseThrow(() -> new ProjectNotFoundException(id));

        project.setName(request.getName());

        project = projectRepository.save(project);

        return projectMapper.toResponse(project);
    }
}