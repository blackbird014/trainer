"""
Simple file system poller for ETL.

Watches a directory for new/modified JSON files and processes them.
"""

import json
import os
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional
from datetime import datetime


class FilePoller:
    """Simple file system poller that watches for JSON files."""
    
    def __init__(self, watch_directory: str, poll_interval: int = 5):
        """
        Initialize file poller.
        
        Args:
            watch_directory: Directory to watch for JSON files
            poll_interval: How often to check for new files (seconds)
        """
        self.watch_directory = Path(watch_directory)
        self.poll_interval = poll_interval
        self.processed_files: Dict[str, float] = {}  # filename -> last modified time
        
        # Create directory if it doesn't exist
        self.watch_directory.mkdir(parents=True, exist_ok=True)
    
    def get_json_files(self) -> List[Path]:
        """Get all JSON files in watch directory."""
        if not self.watch_directory.exists():
            return []
        
        return list(self.watch_directory.glob("*.json"))
    
    def is_new_or_modified(self, file_path: Path) -> bool:
        """Check if file is new or has been modified."""
        filename = str(file_path)
        current_mtime = file_path.stat().st_mtime
        
        if filename not in self.processed_files:
            return True
        
        if current_mtime > self.processed_files[filename]:
            return True
        
        return False
    
    def read_json_file(self, file_path: Path) -> Optional[Dict]:
        """Read and parse JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON file {file_path}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return None
    
    def process_file(self, file_path: Path, callback: Callable[[Dict, Dict], None]):
        """
        Process a single file.
        
        Args:
            file_path: Path to JSON file
            callback: Function to call with (data, metadata)
        """
        if not self.is_new_or_modified(file_path):
            return
        
        data = self.read_json_file(file_path)
        if data is None:
            return
        
        # Create metadata
        metadata = {
            "source": "file_system",
            "file_path": str(file_path),
            "file_name": file_path.name,
            "processed_at": datetime.now().isoformat(),
            "file_size": file_path.stat().st_size
        }
        
        # Call callback
        callback(data, metadata)
        
        # Mark as processed
        self.processed_files[str(file_path)] = file_path.stat().st_mtime
        print(f"✅ Processed: {file_path.name}")
    
    def poll_once(self, callback: Callable[[Dict, Dict], None]):
        """Check for new/modified files and process them."""
        files = self.get_json_files()
        
        for file_path in files:
            self.process_file(file_path, callback)
    
    def poll_continuously(self, callback: Callable[[Dict, Dict], None], stop_event=None):
        """
        Continuously poll for new files.
        
        Args:
            callback: Function to call with (data, metadata)
            stop_event: Optional event to stop polling
        """
        print(f"👀 Watching directory: {self.watch_directory}")
        print(f"⏱️  Poll interval: {self.poll_interval} seconds")
        print("Press Ctrl+C to stop...\n")
        
        try:
            while True:
                self.poll_once(callback)
                
                if stop_event and stop_event.is_set():
                    break
                
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            print("\n🛑 Stopping file poller...")


def example_usage():
    """Example usage of file poller."""
    def process_data(data: Dict, metadata: Dict):
        """Callback function to process data."""
        print(f"📄 Processing file: {metadata['file_name']}")
        print(f"   Data keys: {list(data.keys())}")
        print(f"   Source: {metadata['source']}")
        print()
    
    # Create poller
    poller = FilePoller("data/input", poll_interval=3)
    
    # Poll once (for testing)
    print("=== Polling once ===")
    poller.poll_once(process_data)
    
    # For continuous polling, uncomment:
    # poller.poll_continuously(process_data)


if __name__ == "__main__":
    example_usage()

