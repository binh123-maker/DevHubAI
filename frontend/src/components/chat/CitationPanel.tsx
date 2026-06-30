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
      <ul className="space-y-2">
        {citations.map((citation, idx) => (
          <li key={idx} className="flex items-start bg-white p-2 rounded shadow-sm">
            <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded mr-2 mt-0.5">
              #{idx + 1}
            </span>
            <div>
              <p className="font-medium text-gray-800 truncate" title={citation.document_name}>
                {citation.document_name}
              </p>
              <p className="text-gray-500 text-xs">
                {citation.page_number && `Trang: ${citation.page_number}`}
                {citation.line_start && citation.line_end && ` | Dòng: ${citation.line_start} - ${citation.line_end}`}
              </p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};
