
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,  -- UUID como VARCHAR(36)
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,  -- Contraseña encriptada
    role ENUM('operador', 'inversor') NOT NULL,  -- Define el rol del usuario
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE operations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    operator_id VARCHAR(36) NOT NULL,  -- UUID como VARCHAR(36)
    amount_required DECIMAL(15, 2) NOT NULL,  -- Monto necesario para la operación
    interest_rate DECIMAL(5, 2) NOT NULL,  -- Interés ofrecido por la operación
    deadline DATE NOT NULL,  -- Fecha límite para pujas
    amount_collected DECIMAL(15, 2) DEFAULT 0,  -- Monto recaudado a través de las pujas
    is_closed BOOLEAN DEFAULT FALSE,  -- Indica si la operación está cerrada
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operator_id) REFERENCES users(id) ON DELETE CASCADE
);


CREATE TABLE bids (
    id INT AUTO_INCREMENT PRIMARY KEY,
    operation_id INT NOT NULL,  -- Relaciona con la operación en la que se está pujando
    investor_id VARCHAR(36) NOT NULL,  -- UUID como VARCHAR(36)
    amount DECIMAL(15, 2) NOT NULL,  -- Monto de la puja
    interest_rate DECIMAL(5, 2) NOT NULL,  -- Interés solicitado por el inversor
    bid_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Fecha de la puja
    FOREIGN KEY (operation_id) REFERENCES operations(id) ON DELETE CASCADE,
    FOREIGN KEY (investor_id) REFERENCES users(id) ON DELETE CASCADE
);