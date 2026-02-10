-- Run this SQL to update or insert the 6 inventory items
-- You can run this with: sqlite3 /var/www/html/keytech/database/inventory.db < add_inventory.sql

-- Update or insert each item
INSERT OR REPLACE INTO inventory (id, name, expected, used, tracked) VALUES 
(1, 'Mount Boxes', '960', '959', 'no'),
(2, 'SPR-Install Bags', '818', '813', 'no'),
(3, 'G09-LTMB1VZW', '800', '800', 'no'),
(4, 'Snap-in Holders', '709', '709', 'no'),
(5, 'GPS Units', '0', '0', 'yes'),
(6, 'Card Readers', '0', '0', 'yes');

SELECT 'Database populated with ' || COUNT(*) || ' items' FROM inventory;
SELECT * FROM inventory;