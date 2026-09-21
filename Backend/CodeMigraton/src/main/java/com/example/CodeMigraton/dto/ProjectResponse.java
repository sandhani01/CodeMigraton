package com.example.CodeMigraton.dto;

public class ProjectResponse {
    private Long id ;
    private String name ;

    public ProjectResponse(Long id , String name){
        this.name = name ;
        this.id = id ;
    }

    public void setName(String name){
        this.name = name ;
    }
    public void setId(Long id){
        this.id = id ;
    }
    public String getName(){
        return name ;
    }
    public Long getId(){
        return id ;
    }



}
