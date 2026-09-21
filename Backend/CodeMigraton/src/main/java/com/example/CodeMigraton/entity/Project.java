package com.example.CodeMigraton.entity;

import com.example.CodeMigraton.dto.MigrationResponse;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.*;

import java.util.ArrayList;
import java.util.List;

@Entity
public class Project {

    @OneToMany(
            mappedBy = "project",
            cascade = CascadeType.ALL
    )
    List<Migration> migrations = new ArrayList<>();
    public void addMigrations(Migration migration){
        migrations.add(migration);
        migration.setProject(this);
    }




    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;



    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}