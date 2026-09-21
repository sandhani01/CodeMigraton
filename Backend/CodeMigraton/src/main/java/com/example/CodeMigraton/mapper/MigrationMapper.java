package com.example.CodeMigraton.mapper;

import com.example.CodeMigraton.dto.MigrationResponse;
import com.example.CodeMigraton.entity.Migration;
import org.springframework.stereotype.Component;

@Component
public class MigrationMapper {
    public MigrationResponse toMigrationResponse(Migration migration){
        return  new MigrationResponse(migration.getId(), migration.getProject().getId());

    }
}
