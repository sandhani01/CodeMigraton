package com.example.CodeMigraton.repository;

import com.example.CodeMigraton.entity.Migration;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface MigrationRepository extends JpaRepository<Migration,Long> {
    Page<Migration> findByProjectId(Long projectId, Pageable pageable);
    Page<Migration> findByProjectName(String name,Pageable pageable);
}
