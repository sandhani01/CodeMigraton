package com.example.CodeMigraton.controller;

import com.example.CodeMigraton.dto.MigrationResponse;
import com.example.CodeMigraton.entity.Migration;
import com.example.CodeMigraton.service.MigrationService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;

@RestController
public class MigrationController {
    private final MigrationService migrationService ;
    public MigrationController(MigrationService migrationService){
        this.migrationService = migrationService ;
    }
    @GetMapping("/api/projects/{id}/migrations")
    public ResponseEntity<Page<MigrationResponse>> findByProjectId(@PathVariable Long id , Pageable pageable) {
        return ResponseEntity.ok(migrationService.findByProjectId(id,pageable));
    }
    @GetMapping("/api/projects/migrations")
    public ResponseEntity<Page<MigrationResponse>> findByProjectName(@RequestParam String name , Pageable pageable){
        return ResponseEntity.ok(migrationService.findByProjectName(name,pageable)) ;
    }


        @PostMapping("/api/projects/{projectId}/migrations")
    public ResponseEntity<MigrationResponse> createMigration(@PathVariable Long projectId) {
        MigrationResponse response = migrationService.createMigration(projectId);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
}
