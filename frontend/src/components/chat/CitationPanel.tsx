import React from 'react';
import { Citation } from '../../types/chat.types';

interface CitationPanelProps {
  citations: Citation[];
}

export const CitationPanel: React.FC<CitationPanelProps> = ({ citations }) => {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-2 p-3 bg-gray-50 border border-gray-200 rounded-md text-sm">
      <h4 className="font-semibold text-gray-700 mb-2 flex items-center">
        <svg className="w-4 h-4 mr-1 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Nguồn Trích Dẫn (Citations)
      </h4>
      <ul className="space-y-3">
        {citations.map((citation, idx) => {
          let hostname = citation.document_name;
          let pathname = '';
          if (citation.source_type === 'website' && citation.url) {
            try {
              const urlObj = new URL(citation.url);
              hostname = urlObj.hostname;
              pathname = urlObj.pathname !== '/' ? urlObj.pathname : '';
            } catch (e) {
              // fallback if URL parsing fails
            }
          }

          return (
            <li key={idx} className="flex flex-col bg-white p-3 rounded shadow-sm">
              <div className="flex items-start mb-1">
                <span className="mr-2 mt-0.5">
                  {citation.source_type === 'website' ? '🌐' : '📄'}
                </span>
                <p className="font-medium text-gray-800 break-words flex-1">
                  {citation.source_type === 'website' && citation.url ? (
                    <a href={citation.url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
                      {hostname}
                    </a>
                  ) : (
                    citation.document_name
                  )}
                </p>
              </div>
              
              <div className="text-gray-500 text-xs pl-6 flex flex-col space-y-0.5">
                {citation.source_type === 'website' && pathname && (
                  <span className="font-mono text-[11px] truncate">{pathname}</span>
                )}
                
                {citation.page_number && (
                  <span>Page {citation.page_number}</span>
                )}
                
                {citation.heading && (
                  <span className="text-gray-600 italic">{citation.heading}</span>
                )}
                
                {citation.line_start && citation.line_end && !citation.page_number && !citation.heading && (
                  <span>Lines: {citation.line_start} - {citation.line_end}</span>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};
