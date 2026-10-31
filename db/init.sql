-- Space Bounty Hunters PostgreSQL Initialization Script
-- Creates tables and pre-fills database with initial wanted criminals and hunt logs.

CREATE TABLE IF NOT EXISTS wanted_criminals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    nickname VARCHAR(255) NOT NULL,
    reward DOUBLE PRECISION NOT NULL,
    last_known_coordinates TEXT,
    difficulty INTEGER NOT NULL CHECK (difficulty >= 1 AND difficulty <= 10),
    armed BOOLEAN NOT NULL DEFAULT FALSE,
    has_crew BOOLEAN NOT NULL DEFAULT FALSE,
    escape_master BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_wanted_criminals_nickname ON wanted_criminals(nickname);
CREATE INDEX IF NOT EXISTS idx_wanted_criminals_reward ON wanted_criminals(reward);

CREATE TABLE IF NOT EXISTS hunt_logs (
    id SERIAL PRIMARY KEY,
    criminal_id INTEGER NOT NULL REFERENCES wanted_criminals(id) ON DELETE CASCADE,
    success BOOLEAN NOT NULL,
    notes TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hunt_logs_criminal_id ON hunt_logs(criminal_id);
CREATE INDEX IF NOT EXISTS idx_hunt_logs_created_at ON hunt_logs(created_at);

-- ============================================================================
-- SEED DATA: 7 Wanted Criminals (Requirement: >= 5)
-- ============================================================================
INSERT INTO wanted_criminals (id, name, nickname, reward, last_known_coordinates, difficulty, armed, has_crew, escape_master)
VALUES
    (1, 'Vicious Kane', 'Red Nova', 150000.0, 'Sector 4, Kepler-22b (-14.234, 120.451) - Abandoned titanium refinery', 9, TRUE, TRUE, TRUE),
    (2, 'Lyra Vance', 'Silver Ghost', 85000.0, 'Ganymede Orbital Station (D-Ring, Bay 9)', 7, TRUE, FALSE, TRUE),
    (3, NULL, 'Obsidian Raven', 220000.0, 'Kuiper Belt Outpost 88 (-78.112, 12.903) - Deep freeze sector', 10, TRUE, TRUE, TRUE),
    (4, 'Jaxson Miller', 'Plasma Jack', 45000.0, 'Mars Cydonia Bazaar (Block 14-C)', 5, TRUE, FALSE, FALSE),
    (5, 'Corinne Dubois', 'Viper Queen', 120000.0, 'Europa Sub-ice Colony (-3.882, -45.109)', 8, TRUE, TRUE, FALSE),
    (6, 'Talon Rhyse', 'Rumble', 18000.0, 'Titan Hydrocarbon Docks (Platform 3)', 3, FALSE, TRUE, FALSE),
    (7, NULL, 'Nebula Phantom', 320000.0, 'Orion Nebula Smuggler Corridor (Hyperlane 4)', 10, TRUE, TRUE, TRUE)
ON CONFLICT (id) DO NOTHING;

-- Synchronize serial sequence
SELECT setval('wanted_criminals_id_seq', (SELECT MAX(id) FROM wanted_criminals));

-- ============================================================================
-- SEED DATA: 14 Hunt Journal Logs (Requirement: >= 10)
-- ============================================================================
INSERT INTO hunt_logs (id, criminal_id, success, notes, created_at)
VALUES
    (1, 1, FALSE, 'Ambushed his convoy near Kepler-22b. Target deployed seismic charges and jumped into hyperspace.', NOW() - INTERVAL '14 days'),
    (2, 1, FALSE, 'Cornered in asteroid belt. Escort cruisers returned heavy plasma fire forcing tactical retreat.', NOW() - INTERVAL '12 days'),
    (3, 2, FALSE, 'Detected thermal signature on Ganymede. She hacked docking locks and vented the atmospheric seal.', NOW() - INTERVAL '10 days'),
    (4, 2, TRUE, 'Tracked disguised transport to Io orbit. EMP blast disabled her engines; target placed in cryo-stasis.', NOW() - INTERVAL '9 days'),
    (5, 3, FALSE, 'Traced quantum comms to Kuiper Belt. Raven used a decoy drone with mirrored transponder signature.', NOW() - INTERVAL '8 days'),
    (6, 3, FALSE, 'Heavy laser firefight inside ice tunnels. Target escaped through emergency decompression chute.', NOW() - INTERVAL '7 days'),
    (7, 4, TRUE, 'Intercepted during illegal arms exchange at Mars Cydonia Bazaar. Captured without collateral damage.', NOW() - INTERVAL '6 days'),
    (8, 5, FALSE, 'Sub-ice submarine encounter on Europa. Target released neurotoxin cloud into ventilation.', NOW() - INTERVAL '5 days'),
    (9, 5, FALSE, 'Syndicate reinforcements arrived via stealth corvette before capture protocol could complete.', NOW() - INTERVAL '4 days'),
    (10, 6, TRUE, 'Apprehended at Titan fuel depot after sabotaging his crew''s thruster manifold.', NOW() - INTERVAL '3 days'),
    (11, 7, FALSE, 'Target jammed sensor array using pulsar radiation interference and vanished from radar.', NOW() - INTERVAL '2 days'),
    (12, 7, FALSE, 'Long-range pursuit through Orion Nebula dust clouds; lost contact due to ionic storm.', NOW() - INTERVAL '1 day'),
    (13, 4, FALSE, 'Earlier attempt on Phobos: Jack detonated an ammo crate, causing brief distraction and escaped.', NOW() - INTERVAL '18 hours'),
    (14, 1, FALSE, 'Spotted at a neutral refueling station on Ceres; escaped on an unregistered smuggling skiff.', NOW() - INTERVAL '6 hours')
ON CONFLICT (id) DO NOTHING;

-- Synchronize serial sequence
SELECT setval('hunt_logs_id_seq', (SELECT MAX(id) FROM hunt_logs));
