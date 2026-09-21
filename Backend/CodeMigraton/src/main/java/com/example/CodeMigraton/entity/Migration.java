package com.example.CodeMigraton.entity;


import jakarta.persistence.*;

@Entity
public class Migration {
    @Id
    @GeneratedValue(strategy =  GenerationType.IDENTITY)
    private Long id ;

    @ManyToOne
    @JoinColumn(name = "project_id")
    private Project project ;

    public Long getId() {
        return id;
    }

    public Project getProject() {
        return project;
    }

    public void setProject(Project project){
        this.project = project ;
    }
}
