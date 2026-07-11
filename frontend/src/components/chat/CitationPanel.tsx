import React from 'react';
import { Citation } from '../../types/chat.types';

interface CitationPanelProps {
  citations: Citation[];
}

export const CitationPanel: React.FC<CitationPanelProps> = ({ citations }) => {
  if (!citations || citations.length === 0) return null;

  // Group by document name to display each unique source document only once
  const uniqueCitations = React.useMemo(() => {
    const seen = new Set<string>();
    const result: Citation[] = [];
    for (const c of citations) {
      if (!c.document_name) continue;
      if (!seen.has(c.document_name)) {
        seen.add(c.document_name);
        result.push(c);
      }
    }
    return result;
  }, [citations]);

  // Truncate filenames exceeding 24 characters with an ellipsis
  const truncateFilename = (filename: string, maxLen = 24): string => {
    if (filename.length <= maxLen) return filename;
    return filename.substring(0, maxLen - 3) + '...';
  };

  return (
    <div className="mt-1 text-xs text-muted-foreground">
      <div className="font-semibold text-gray-500 mb-1">Nguồn:</div>
      <ul className="space-y-1 pl-1">
        {uniqueCitations.map((citation, idx) => {
          const isWeb = citation.source_type === 'website' && citation.url;
          const displayLabel = truncateFilename(citation.document_name);

          return (
            <li 
              key={idx} 
              className="flex items-center text-gray-600 hover:text-gray-800 transition-colors"
              title={citation.document_name}
            >
              <span className="text-gray-400 mr-2 font-mono">[{idx + 1}]</span>
              {isWeb ? (
                <a 
                  href={citation.url} 
                  target="_blank" 
                  rel="noreferrer" 
                  className="text-blue-500 hover:text-blue-700 hover:underline cursor-pointer font-medium"
                >
                  {displayLabel}
                </a>
              ) : (
                <span className="font-medium select-all">
                  {displayLabel}
                </span>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
};
