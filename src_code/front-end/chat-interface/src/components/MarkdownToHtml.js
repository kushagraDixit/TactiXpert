import React from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const MarkdownToHtml = ({ markdownText }) => {
  // Convert markdown to HTML
  const rawHtml = marked(markdownText);
  
  // Sanitize the HTML to prevent XSS
  const sanitizedHtml = DOMPurify.sanitize(rawHtml);

  return (
    <div className="team-strength-content" dangerouslySetInnerHTML={{ __html: sanitizedHtml }} />
  );
};

export default MarkdownToHtml;
