-- Database Initialization Script
-- Creates the structure for the drawings database and adds initial seed data.

USE planos_telescopio;

CREATE TABLE IF NOT EXISTS drawings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    catalog_code VARCHAR(100) NOT NULL,
    piece_name VARCHAR(255) NOT NULL,
    material VARCHAR(255) NOT NULL,
    author_initials VARCHAR(50) NOT NULL,
    author_date VARCHAR(50) NOT NULL,
    enlace VARCHAR(500) NULL
);

-- Seed mock data for verification
INSERT INTO drawings (catalog_code, piece_name, material, author_initials, author_date, enlace) VALUES
('T2.5-001', 'Soporte del Espejo Primario', 'Acero Inoxidable', 'JD', '2026-01-15', 'https://www.not.iac.es/telescope/drawings/T2.5-001_Mirror_Support.jpeg'),
('T2.5-002', 'Montura del Espejo Secundario', 'Fibra de Carbono', 'EM', '2026-02-10', 'https://www.not.iac.es/telescope/drawings/T2.5-002_Secondary_Mirror.jpeg'),
('A1.0-050', 'Placa Adaptadora del Telescopio', 'Aluminio 6061-T6', 'AN', '2026-03-01', NULL),
('W0.1-010', 'Soporte del Anemómetro', 'Acero Galvanizado', 'JD', '2026-04-18', NULL),
('FM2.5-102', 'Engranaje de la Rueda de Filtros', 'Bronce', 'RC', '2026-05-02', 'https://www.not.iac.es/telescope/drawings/FM2.5-102_Filter_Wheel.jpeg');
