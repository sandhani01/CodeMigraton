package com.example.CodeMigraton.dto;


import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class ProjectCreateRequest {
    @NotBlank
    @Size(min = 3)
    private String name ;
    ProjectCreateRequest(String name){
        this.name = name ;
    }
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
