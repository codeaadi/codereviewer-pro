import re 
from typing import List, Dict, Any

class GitDiffParser:
    """
    Parses unified git diff output into strutured file chunks with line tracking.
    """
    DIFF_FILE_HEADER = re.compile(r'^diff --git a/(.*) b/(.*)')
    HUNK_HEADER = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')
    
    @staticmethod
    def parse(raw_diff: str) -> List[Dict[str, Any]]:
        files = []
        current_file = None
        current_hunk = None
        new_line_num = 0
        
        for line in raw_diff.splitlines():
            file_match = GitDiffParser.DIFF_FILE_HEADER.match(line)
            if file_match:
                if current_file:
                    if current_hunk:
                        current_file['hunks'].append(current_hunk)
                    files.append(current_file)
                current_file = {
                    'old_path': file_match.group(1),
                    'new_path': file_match.group(2),
                    'hunks': [],
                    'raw_content': []
                }
                current_hunk = None
                continue
            
            if not current_file:
                continue 
            
            current_file['raw_content'].append(line)
            
            hunk_match = GitDiffParser.HUNK_HEADER.match(line)
            if hunk_match:
                if current_hunk:
                    current_file['hunks'].append(current_hunk)
                new_line_num = int(hunk_match.group(3))
                current_hunk = {
                    'header': line,
                    'start_line': new_line_num,
                    'lines' : []
                }
                continue
            
            if current_hunk:
                if line.startswith('+') and not line.startswith('+++'):
                    current_hunk['lines'].append({
                        'type': 'added',
                        'line_num': new_line_num,
                        'text': line[1:]
                    })
                    new_line_num += 1 
                elif line.startswith('+') and not line.startswith('+++'):
                    current_hunk['lines'].append({
                        'type': 'added',
                        'line_num': new_line_num,
                        'text': line[1:]
                    })
                    new_line_num += 1 
                elif line.startswith('-') and not line.startswith('---'):
                    current_hunk['lines'].append({
                        'type': 'deleted',
                        "line_num": None,
                        'text': line[1:]
                    })
                else:
                    current_hunk['lines'].append({
                        'type': 'context',
                        'line_num': new_line_num,
                        'text': line[1:] if line.startswith(' ') else line
                    })
                    new_line_num += 1
                    
        if current_file:
            if current_hunk:
                current_file['hunks'].append(current_hunk)
            files.append(current_file)
            
        return files
                    
            