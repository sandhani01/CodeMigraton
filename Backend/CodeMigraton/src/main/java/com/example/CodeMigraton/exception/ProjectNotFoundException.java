package com.example.CodeMigraton.exception;

public class ProjectNotFoundException extends RuntimeException{
    public ProjectNotFoundException(Long id){
        super("Project Not Found With ID : "+id);
    }
}