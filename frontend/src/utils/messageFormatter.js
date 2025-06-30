/**
 * Utility functions for formatting chat messages
 */

// Regular expression to match markdown code blocks
const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;

/**
 * Parse a message content and extract code blocks
 * @param {string} content - The message content to parse
 * @returns {Array} - Array of content segments (text or code blocks)
 */
export const parseMessageContent = (content) => {
  if (!content) return [];
  
  const segments = [];
  let lastIndex = 0;
  let match;
  
  // Reset regex to start from the beginning
  codeBlockRegex.lastIndex = 0;
  
  while ((match = codeBlockRegex.exec(content)) !== null) {
    // Add text before code block
    if (match.index > lastIndex) {
      segments.push({
        type: 'text',
        content: content.substring(lastIndex, match.index)
      });
    }
    
    // Add code block
    segments.push({
      type: 'code',
      language: match[1] || '',
      content: match[2]
    });
    
    lastIndex = match.index + match[0].length;
  }
  
  // Add remaining text after last code block
  if (lastIndex < content.length) {
    segments.push({
      type: 'text',
      content: content.substring(lastIndex)
    });
  }
  
  // If no code blocks were found, return the entire content as text
  if (segments.length === 0) {
    segments.push({
      type: 'text',
      content
    });
  }
  
  return segments;
};

/**
 * Format text content with markdown-like syntax
 * @param {string} text - The text content to format
 * @returns {string} - HTML formatted text
 */
export const formatTextContent = (text) => {
  if (!text) return '';
  
  // Replace URLs with links
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  text = text.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:underline">$1</a>');
  
  // Replace inline code with styled spans
  const inlineCodeRegex = /`([^`]+)`/g;
  text = text.replace(inlineCodeRegex, '<code class="bg-gray-100 text-red-600 px-1 py-0.5 rounded font-mono text-sm">$1</code>');
  
  // Replace bold text
  const boldRegex = /\*\*([^*]+)\*\*/g;
  text = text.replace(boldRegex, '<strong>$1</strong>');
  
  // Replace italic text
  const italicRegex = /\*([^*]+)\*/g;
  text = text.replace(italicRegex, '<em>$1</em>');
  
  // Replace newlines with <br>
  text = text.replace(/\n/g, '<br>');
  
  return text;
};

/**
 * Detect if a message contains code
 * @param {string} content - The message content to check
 * @returns {boolean} - True if the message contains code blocks
 */
export const messageContainsCode = (content) => {
  if (!content) return false;
  return codeBlockRegex.test(content);
};

/**
 * Extract file references from a message
 * @param {string} content - The message content to parse
 * @returns {Array} - Array of file references
 */
export const extractFileReferences = (content) => {
  if (!content) return [];
  
  const fileRegex = /(?:in|from|file|path)\s+[`"']?([\/\w\-\.]+\.\w+)[`"']?/gi;
  const matches = [...content.matchAll(fileRegex)];
  
  return matches.map(match => match[1]);
};