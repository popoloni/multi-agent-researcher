import React, { useState } from 'react';
import { Clipboard, Check } from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-jsx';
import 'prismjs/components/prism-tsx';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-java';
import 'prismjs/components/prism-c';
import 'prismjs/components/prism-cpp';
import 'prismjs/components/prism-csharp';
import 'prismjs/components/prism-go';
import 'prismjs/components/prism-rust';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-yaml';
import 'prismjs/components/prism-markdown';
import 'prismjs/components/prism-sql';
import 'prismjs/components/prism-ruby';
import 'prismjs/components/prism-php';
import 'prismjs/components/prism-swift';
import 'prismjs/components/prism-kotlin';
import 'prismjs/components/prism-scala';
import 'prismjs/components/prism-dart';

// Initialize Prism
if (typeof window !== 'undefined') {
  Prism.manual = true;
}

const CodeBlock = ({ code, language, fileName, lineNumbers = true }) => {
  const [copied, setCopied] = useState(false);

  // Determine language for syntax highlighting
  const getLanguage = () => {
    if (!language) {
      // Try to detect from file extension if fileName is provided
      if (fileName) {
        const ext = fileName.split('.').pop()?.toLowerCase();
        const extMap = {
          'js': 'javascript',
          'ts': 'typescript',
          'jsx': 'jsx',
          'tsx': 'tsx',
          'py': 'python',
          'java': 'java',
          'c': 'c',
          'cpp': 'cpp',
          'cs': 'csharp',
          'go': 'go',
          'rs': 'rust',
          'sh': 'bash',
          'json': 'json',
          'yml': 'yaml',
          'yaml': 'yaml',
          'md': 'markdown',
          'sql': 'sql',
          'rb': 'ruby',
          'php': 'php',
          'swift': 'swift',
          'kt': 'kotlin',
          'scala': 'scala',
          'dart': 'dart',
        };
        return extMap[ext] || 'javascript';
      }
      return 'javascript'; // Default
    }
    return language;
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Apply syntax highlighting
  let highlightedCode;
  try {
    highlightedCode = Prism.highlight(
      code,
      Prism.languages[getLanguage()] || Prism.languages.javascript,
      getLanguage()
    );
  } catch (error) {
    // Fallback for test environment or when Prism fails
    console.warn('Prism highlighting failed:', error);
    highlightedCode = code;
  }

  return (
    <div className="relative rounded-lg overflow-hidden my-4 bg-gray-800 text-white">
      {/* Header with filename and copy button */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-700 text-gray-200">
        <div className="text-sm font-mono">
          {fileName || getLanguage()}
        </div>
        <button
          onClick={handleCopyCode}
          className="text-gray-300 hover:text-white focus:outline-none"
          title="Copy code"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-400" />
          ) : (
            <Clipboard className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Code content */}
      <div className="overflow-x-auto p-4">
        {lineNumbers ? (
          <pre className="language-{getLanguage()}">
            <code
              dangerouslySetInnerHTML={{ __html: highlightedCode }}
              className={`language-${getLanguage()}`}
            />
          </pre>
        ) : (
          <pre>
            <code
              dangerouslySetInnerHTML={{ __html: highlightedCode }}
              className={`language-${getLanguage()}`}
            />
          </pre>
        )}
      </div>
    </div>
  );
};

export default CodeBlock;