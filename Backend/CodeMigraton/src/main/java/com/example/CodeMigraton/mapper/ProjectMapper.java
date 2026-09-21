package com.example.CodeMigraton.mapper;

import com.example.CodeMigraton.dto.MigrationResponse;
import com.example.CodeMigraton.dto.ProjectResponse;
import com.example.CodeMigraton.entity.Migration;
import com.example.CodeMigraton.entity.Project;
import org.springframework.stereotype.Component;

@Component
public class ProjectMapper {
    public ProjectResponse toResponse(Project project){
        return new ProjectResponse(project.getId(), project.getName());
    }
}
