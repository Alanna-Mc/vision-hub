-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- ROLES --

CREATE TABLE roles (
    roleId INTEGER PRIMARY KEY AUTOINCREMENT,
    roleName TEXT UNIQUE NOT NULL
);

INSERT INTO roles (roleName) VALUES ('Admin'), ('Manager'), ('Staff');

-- USERS --

CREATE TABLE users (
    userId INTEGER PRIMARY KEY AUTOINCREMENT,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    passwordHash TEXT NOT NULL,
    roleId INTEGER NOT NULL,
    FOREIGN KEY (roleId) REFERENCES roles (roleId)
);
 
-- temp default admin user
INSERT INTO users (firstName, lastName, email, passwordHash, roleId) VALUES (
    'Tom', 'Goodwin', 'admin@visionhub.com', 'adminpass',
    (SELECT roleId FROM roles WHERE roleName = 'Admin')
);




