package com.example.CodeMigraton.service;

import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class CustomUserDetailsService implements UserDetailsService {
    private final PasswordEncoder passwordEncoder ;
    public CustomUserDetailsService(PasswordEncoder passwordEncoder){
        this.passwordEncoder = passwordEncoder ;
    }

    @Override
    public UserDetails loadUserByUsername(String username){
        return User.withUsername("Sandhani").password(passwordEncoder.encode("Shaaza")).roles("USER").build();
    }
}
