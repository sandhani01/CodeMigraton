package com.example.CodeMigraton.service;
import com.example.CodeMigraton.dto.MigrationResponse;
import com.example.CodeMigraton.entity.Migration;
import com.example.CodeMigraton.entity.Project;
import com.example.CodeMigraton.exception.ProjectNotFoundException;
import com.example.CodeMigraton.mapper.MigrationMapper;
import com.example.CodeMigraton.repository.MigrationRepository;
import com.example.CodeMigraton.repository.ProjectRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class MigrationService {
    private final MigrationRepository migrationRepository ;
    private  final ProjectRepository projectRepository ;
    private final MigrationMapper migrationMapper;

    public MigrationService(MigrationMapper migrationMapper , ProjectRepository projectRepository,MigrationRepository migrationRepository){
        this.migrationRepository = migrationRepository ;
        this.projectRepository = projectRepository ;
        this.migrationMapper = migrationMapper ;
    }

    public MigrationResponse createMigration(Long projectId) {
        Project project = projectRepository.findById(projectId).orElseThrow(()-> new ProjectNotFoundException(projectId));
        Migration migration = new Migration();
        project.addMigrations(migration);
        Migration updated = migrationRepository.save(migration);
        return migrationMapper.toMigrationResponse(migration);
    }
    public Page<MigrationResponse> findByProjectId(Long id, Pageable pageable) {
        Page<Migration> migration = migrationRepository.findByProjectId(id,pageable);
        return migration.map(migrationMapper::toMigrationResponse);

    }
    public List<Migration> giveAllMigrations(){
        return migrationRepository.findAll();
    }

    public Page<MigrationResponse> findByProjectName(String name , Pageable pageable){
        Page<Migration> migration = migrationRepository.findByProjectName(name,pageable);
        return migration.map(migrationMapper::toMigrationResponse);
    }
}
