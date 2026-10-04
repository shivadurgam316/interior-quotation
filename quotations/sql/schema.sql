CREATE TABLE IF NOT EXISTS quotation_company (
    id INT NOT NULL AUTO_INCREMENT,
    company_name VARCHAR(255) NOT NULL,
    address TEXT NULL,
    phone VARCHAR(50) NULL,
    email VARCHAR(255) NULL,
    gst_number VARCHAR(50) NULL,
    logo_path VARCHAR(500) NULL,
    signature_path VARCHAR(500) NULL,
    terms_conditions TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS quotation_customer (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    whatsapp_number VARCHAR(30) NOT NULL,
    email VARCHAR(255) NULL,
    address TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_customer_name (name),
    INDEX idx_customer_whatsapp (whatsapp_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS quotation_product (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NULL,
    unit VARCHAR(30) NOT NULL DEFAULT 'NOS',
    default_price DECIMAL(15,2) NOT NULL DEFAULT 0,
    tax_percentage DECIMAL(5,2) NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_product_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS quotation_sequence (
    id INT NOT NULL,
    last_number INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO quotation_sequence (id, last_number)
VALUES (1, 0)
ON DUPLICATE KEY UPDATE id = id;

CREATE TABLE IF NOT EXISTS quotation (
    id INT NOT NULL AUTO_INCREMENT,
    quotation_number VARCHAR(50) NOT NULL,
    customer_id INT NOT NULL,
    quotation_date DATE NOT NULL,
    subtotal DECIMAL(15,2) NOT NULL DEFAULT 0,
    sgst DECIMAL(15,2) NOT NULL DEFAULT 0,
    cgst DECIMAL(15,2) NOT NULL DEFAULT 0,
    grand_total DECIMAL(15,2) NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
    terms_conditions TEXT NULL,
    pdf_path VARCHAR(500) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_quotation_number (quotation_number),
    INDEX idx_quotation_customer (customer_id),
    CONSTRAINT fk_quotation_customer
        FOREIGN KEY (customer_id)
        REFERENCES quotation_customer(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS quotation_item (
    id INT NOT NULL AUTO_INCREMENT,
    quotation_id INT NOT NULL,
    description VARCHAR(500) NOT NULL,
    quantity DECIMAL(15,2) NOT NULL DEFAULT 0,
    unit VARCHAR(30) NOT NULL DEFAULT 'NOS',
    price DECIMAL(15,2) NOT NULL DEFAULT 0,
    total DECIMAL(15,2) NOT NULL DEFAULT 0,
    tax_percentage DECIMAL(5,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    INDEX idx_item_quotation (quotation_id),
    CONSTRAINT fk_item_quotation
        FOREIGN KEY (quotation_id)
        REFERENCES quotation(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS quotation_delivery_log (
    id INT NOT NULL AUTO_INCREMENT,
    quotation_id INT NOT NULL,
    channel VARCHAR(30) NOT NULL,
    recipient VARCHAR(255) NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    message_id VARCHAR(255) NULL,
    error_message TEXT NULL,
    sent_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_delivery_quotation (quotation_id),
    CONSTRAINT fk_delivery_quotation
        FOREIGN KEY (quotation_id)
        REFERENCES quotation(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO quotation_company
    (company_name, address, terms_conditions)
SELECT
    'Vanara Projects',
    '# Bollaram Road, Miyapur, Hyderabad, Telangana',
    '1. Goods once sold will not be taken back or exchanged.
2. Advance payment of 50% before work starts.
3. 30% payment amount on completion of 35% work.
4. 20% payment amount on completion of 100% work.
5. Additional charges will apply for any structural changes or modifications.
6. This is an estimated quote (approximate value).'
WHERE NOT EXISTS (SELECT 1 FROM quotation_company);
