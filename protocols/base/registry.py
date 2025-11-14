"""Protocol registry for managing available test protocols."""

from typing import Dict, List, Optional
from pathlib import Path
from .protocol import Protocol


class ProtocolRegistry:
    """Registry for managing and accessing test protocols."""

    def __init__(self):
        """Initialize the protocol registry."""
        self._protocols: Dict[str, Protocol] = {}
        self._protocol_paths: Dict[str, Path] = {}

    def register(self, protocol: Protocol) -> None:
        """Register a protocol.

        Args:
            protocol: Protocol instance to register
        """
        protocol_id = protocol.protocol_id
        self._protocols[protocol_id] = protocol
        self._protocol_paths[protocol_id] = protocol.json_path

    def register_from_file(self, json_path: Path) -> Protocol:
        """Load and register a protocol from a JSON file.

        Args:
            json_path: Path to the protocol JSON file

        Returns:
            The registered Protocol instance
        """
        protocol = Protocol(json_path)
        self.register(protocol)
        return protocol

    def register_from_directory(self, directory: Path, recursive: bool = True) -> int:
        """Scan a directory and register all protocol JSON files.

        Args:
            directory: Directory to scan for protocol files
            recursive: Whether to scan subdirectories recursively

        Returns:
            Number of protocols registered
        """
        count = 0
        pattern = "**/*.json" if recursive else "*.json"

        for json_file in directory.glob(pattern):
            try:
                self.register_from_file(json_file)
                count += 1
            except Exception as e:
                print(f"Warning: Failed to load protocol from {json_file}: {e}")

        return count

    def get(self, protocol_id: str) -> Optional[Protocol]:
        """Get a protocol by ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol instance or None if not found
        """
        return self._protocols.get(protocol_id)

    def list_protocols(self) -> List[Dict[str, str]]:
        """List all registered protocols.

        Returns:
            List of protocol summaries
        """
        return [
            {
                'protocol_id': p.protocol_id,
                'name': p.name,
                'version': p.version,
                'category': p.category
            }
            for p in self._protocols.values()
        ]

    def get_by_category(self, category: str) -> List[Protocol]:
        """Get all protocols in a specific category.

        Args:
            category: Category name

        Returns:
            List of protocols in the category
        """
        return [
            p for p in self._protocols.values()
            if p.category.lower() == category.lower()
        ]

    def clear(self) -> None:
        """Clear all registered protocols."""
        self._protocols.clear()
        self._protocol_paths.clear()

    def __len__(self) -> int:
        """Get number of registered protocols."""
        return len(self._protocols)

    def __contains__(self, protocol_id: str) -> bool:
        """Check if protocol is registered."""
        return protocol_id in self._protocols
