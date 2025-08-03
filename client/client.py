import argparse
import subprocess
import sys
from typing import Dict, List, Optional
from urllib.parse import urlparse
import requests

class BookmarkClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        
    def get_bookmarks(self) -> List[Dict]:
        """Fetch all bookmarks from the API"""
        try:
            response = requests.get(f"{self.base_url}/bookmarks")
            response.raise_for_status()
            result = response.json()
            return result.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching bookmarks: {e}", file=sys.stderr)
            return []
    
    def add_bookmark(self, url: str, label: str) -> bool:
        """Add a new bookmark"""
        try:
            data = {"url": url, "label": label}
            response = requests.post(f"{self.base_url}/bookmarks", json=data)
            if response.status_code == 409:
                print(response.json()['detail'])
                return True
            response.raise_for_status()
            print(f"✓ Added bookmark: {label}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error adding bookmark: {e}", file=sys.stderr)
            return False
    
    def delete_bookmark(self, bookmark_id: int) -> bool:
        """Delete a bookmark by ID"""
        try:
            response = requests.delete(f"{self.base_url}/bookmarks/{bookmark_id}")
            response.raise_for_status()
            print(f"✓ Deleted bookmark with ID: {bookmark_id}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting bookmark: {e}", file=sys.stderr)
            return False

def format_bookmark_for_fzf(bookmark: Dict, max_label_width: int = 20) -> str:
    """Format bookmark for FZF display with better alignment"""
    bookmark_id = str(bookmark.get('id', 'N/A'))
    label = bookmark.get('label', 'No Label')
    url = bookmark.get('url', 'No URL')
    
    # Truncate label if too long, add ellipsis
    if len(label) > max_label_width:
        label = label[:max_label_width-3] + "..."
    
    # Format with consistent spacing
    # [ID] Label (padded to max_label_width) │ URL
    id_part = f"[{bookmark_id}]"  # Right-align ID with width 3
    label_part = f"{label:<{max_label_width}}"  # Left-align label
    
    return f"{id_part}\t{label_part}\t│ {url}"

def parse_fzf_selection(selection: str) -> Dict:
    """Parse the selected line from FZF back to bookmark data"""
    try:
        # Extract ID from [ID] format
        id_part = selection.split(']')[0][1:].strip()  # Remove '[' and ']', strip whitespace
        bookmark_id = int(id_part)
        
        # Extract label and URL using the │ separator
        rest = selection.split('\t', 1)[1]
        label, url = rest.split('\t│', 1)
        label = label.strip()  # Remove padding spaces
        return {
            'id': bookmark_id,
            'label': label,
            'url': url.strip()
        }
    except (ValueError, IndexError) as e:
        print(f"Error parsing selection: {e}", file=sys.stderr)
        return {}

def run_fzf(items: List[str], prompt: str = "Select bookmark: ") -> Optional[str]:
    """Run FZF with the given items and return the selection"""
    if not items:
        print("No bookmarks found", file=sys.stderr)
        return None
    
    try:

        fzf_options = [
            'fzf',
            '--prompt', prompt,
            '--height', '40%',
            '--reverse',
            # '--info=inline',
            # '--preview-window=wrap',
            '--header=ID\tLabel\t\t\t│ URL',
            '--header-lines=0'
        ]
        # Run fzf with the items
        process = subprocess.Popen(
            fzf_options,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input='\n'.join(items))
        
        if process.returncode == 0:
            return stdout.strip()
        elif process.returncode == 1:  # User cancelled
            return None
        else:
            print(f"FZF error: {stderr}", file=sys.stderr)
            return None
            
    except FileNotFoundError:
        print("Error: fzf not found. Please install fzf first.", file=sys.stderr)
        return None

def search_bookmarks(client: BookmarkClient):
    """Interactive bookmark search using FZF"""
    bookmarks = client.get_bookmarks()
    if not bookmarks:
        print("No bookmarks found")
        return
    
    # Format bookmarks for FZF
    fzf_items = [format_bookmark_for_fzf(bm) for bm in bookmarks]
    
    # Run FZF
    selection = run_fzf(fzf_items, "Search bookmarks: ")
    
    if selection:
        bookmark = parse_fzf_selection(selection)
        if bookmark:
            print("\n📌 Selected Bookmark:")
            print(f"   ID: {bookmark['id']}")
            print(f"   Label: {bookmark['label']}")
            print(f"   URL: {bookmark['url']}")
            
            # Ask what to do with the selection
            action = input("\n[o]pen URL, [c]opy URL, [d]elete, or [Enter] to exit: ").lower()
            
            if action == 'o':
                open_url(bookmark['url'])
            elif action == 'c':
                copy_to_clipboard(bookmark['url'])
            elif action == 'd':
                confirm = input(f"Delete '{bookmark['label']}'? [y/N]: ")
                if confirm.lower() == 'y':
                    client.delete_bookmark(bookmark['id'])

def open_url(url: str):
    """Open URL in default browser"""
    try:
        import webbrowser
        webbrowser.open(url)
        print(f"✓ Opened {url}")
    except Exception as e:
        print(f"Error opening URL: {e}", file=sys.stderr)

def copy_to_clipboard(text: str):
    """Copy text to clipboard"""
    try:
        # Try different clipboard commands
        commands = [
            ['xclip', '-selection', 'clipboard'],  # Linux
            ['pbcopy'],  # macOS
            ['clip']  # Windows
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, input=text, text=True, check=True)
                print(f"✓ Copied to clipboard: {text}")
                return
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        print("Could not copy to clipboard (no suitable command found)", file=sys.stderr)
        
    except Exception as e:
        print(f"Error copying to clipboard: {e}", file=sys.stderr)

def list_bookmarks(client: BookmarkClient):
    """List all bookmarks in a simple format"""
    bookmarks = client.get_bookmarks()
    if not bookmarks:
        print("No bookmarks found")
        return
    
    print(f"📚 Found {len(bookmarks)} bookmarks:\n")
    for bm in bookmarks:
        print(f"[{bm.get('id', 'N/A')}] {bm.get('label', 'No Label')}")
        print(f"\t{bm.get('url', 'No URL')}\n")

def add_bookmark_interactive(client: BookmarkClient):
    """Interactive bookmark addition"""
    url = input("Enter URL: ").strip()
    if not url:
        print("URL cannot be empty")
        return
    
    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = f"https://{url}"
    except Exception:
        pass
    
    label = input("Enter label (optional): ").strip()
    if not label:
        # Generate label from URL
        try:
            parsed = urlparse(url)
            label = parsed.netloc or url
        except Exception:
            label = url
    
    client.add_bookmark(url, label)

def main():
    parser = argparse.ArgumentParser(description="Bookmark CLI Client with FZF")
    parser.add_argument('--server', default='http://localhost:8000', 
                       help='FastAPI server URL (default: http://localhost:8000)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command (default)
    subparsers.add_parser('search', help='Search bookmarks with FZF (default)')
    
    # List command
    subparsers.add_parser('list', help='List all bookmarks')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new bookmark')
    add_parser.add_argument('url', nargs='?', help='URL to bookmark')
    add_parser.add_argument('label', nargs='?', help='Label for the bookmark')
    
    args = parser.parse_args()
    
    client = BookmarkClient(args.server)
    
    # Default to search if no command specified
    command = args.command or 'search'
    
    if command == 'search':
        search_bookmarks(client)
    elif command == 'list':
        list_bookmarks(client)
    elif command == 'add':
        if args.url:
            label = args.label or args.url
            client.add_bookmark(args.url, label)
        else:
            add_bookmark_interactive(client)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()