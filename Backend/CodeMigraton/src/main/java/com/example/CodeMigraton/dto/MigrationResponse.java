package com.example.CodeMigraton.dto;

public class MigrationResponse {

    private Long id;
    private Long projectId;

    public MigrationResponse(Long id, Long projectId) {
        this.id = id;
        this.projectId = projectId;
    }

    public Long getId() {
        return id;
    }

    public Long getProjectId() {
        return projectId;
    }
}