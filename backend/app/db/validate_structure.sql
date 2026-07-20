-- Distinct Node Types
SELECT node_type, COUNT(*) 
FROM document_structure_nodes 
GROUP BY node_type 
ORDER BY COUNT(*) DESC;

-- Metadata Completeness Checks
SELECT id, node_type, metadata_json 
FROM document_structure_nodes 
WHERE metadata_json IS NULL 
   OR NOT (metadata_json ? 'word_count')
   OR NOT (metadata_json ? 'token_estimate')
   OR NOT (metadata_json ? 'heading_path')
   OR NOT (metadata_json ? 'section_path')
   OR NOT (metadata_json ? 'contains_code')
   OR NOT (metadata_json ? 'contains_table')
   OR NOT (metadata_json ? 'contains_list')
   OR NOT (metadata_json ? 'reading_time')
   OR NOT (metadata_json ? 'keywords');

-- Heading Hierarchy Check
SELECT id, node_type, parent_id, hierarchy_level 
FROM document_structure_nodes 
WHERE node_type LIKE 'heading_%' 
  AND hierarchy_level = 0;

-- Invalid Parent Relationships
SELECT child.id, child.parent_id 
FROM document_structure_nodes child 
LEFT JOIN document_structure_nodes parent ON child.parent_id = parent.id 
WHERE child.parent_id IS NOT NULL 
  AND parent.id IS NULL;

-- Nodes without Paths
SELECT id, node_type, metadata_json->'heading_path' AS heading_path 
FROM document_structure_nodes 
WHERE metadata_json->'heading_path' IS NULL;
