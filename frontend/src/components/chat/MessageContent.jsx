import React from 'react';
import CodeBlock from './CodeBlock';
import SourceReference from './SourceReference';
import { parseMessageContent, formatTextContent } from '../../utils/messageFormatter';

const MessageContent = ({ message, onViewSource }) => {
  if (!message || !message.content) {
    return null;
  }

  // Parse message content to extract code blocks
  const segments = parseMessageContent(message.content);

  return (
    <div className="message-content">
      {segments.map((segment, index) => {
        if (segment.type === 'code') {
          return (
            <CodeBlock
              key={index}
              code={segment.content}
              language={segment.language}
              lineNumbers={true}
            />
          );
        } else {
          return (
            <div 
              key={index}
              className="prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: formatTextContent(segment.content) }}
            />
          );
        }
      })}

      {/* Display sources if available */}
      {message.sources && message.sources.length > 0 && (
        <SourceReference 
          sources={message.sources} 
          onViewSource={onViewSource} 
        />
      )}
    </div>
  );
};

export default MessageContent;