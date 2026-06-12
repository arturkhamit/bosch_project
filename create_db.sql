CREATE TYPE inspection_result AS ENUM ('PASS', 'FAIL', 'WARNING');

CREATE TYPE defect_severity AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

CREATE TYPE defect_status AS ENUM ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED');


CREATE TABLE product
(
    id BIGINT PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    product_family VARCHAR(100),
    revision VARCHAR(30),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE inspector
(
    id BIGINT PRIMARY KEY,
    employee_number VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    department VARCHAR(100),
    role VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE inspection
(
    id BIGINT PRIMARY KEY,
    batch_number VARCHAR(50) NOT NULL,
    serial_number VARCHAR(100) NOT NULL,
    inspection_date TIMESTAMP NOT NULL,
    result inspection_result NOT NULL,
    notes TEXT,
    product_id BIGINT NOT NULL,
    inspector_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id) REFERENCES product(id),
    FOREIGN KEY (inspector_id) REFERENCES inspector(id)
);


CREATE TABLE defect
(
    id BIGINT PRIMARY KEY,
    defect_code VARCHAR(50) NOT NULL,
    defect_type VARCHAR(100) NOT NULL,
    severity defect_severity NOT NULL,
    status defect_status NOT NULL,
    description TEXT NOT NULL,
    detected_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    root_cause TEXT,
    corrective_action TEXT,
    product_id BIGINT NOT NULL,
    inspection_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id) REFERENCES product(id),
    FOREIGN KEY (inspection_id) REFERENCES inspection(id)
);