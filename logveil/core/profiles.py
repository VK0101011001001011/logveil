"""
LogVeil Profile System
Manages redaction profiles for different log types and environments.
"""

import json
import yaml
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class LogFormat(Enum):
    """Supported log formats."""
    PLAINTEXT = "plaintext"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    XML = "xml"
    STRUCTURED = "structured"


@dataclass
class RedactionRule:
    """Defines a redaction rule."""
    pattern: str
    replacement: str
    confidence: float = 1.0
    enabled: bool = True
    description: Optional[str] = None


@dataclass
class KeyPathRule:
    """Redaction rule for structured data key paths."""
    key_path: str  # e.g., "user.email", "auth.*.token"
    action: str = "redact"  # redact, remove, mask
    replacement: Optional[str] = None


@dataclass
class RedactionProfile:
    """A complete redaction profile for a specific log type."""
    name: str
    description: str
    log_format: LogFormat
    patterns: List[RedactionRule]
    key_paths: List[KeyPathRule]
    entropy_config: Dict[str, Any]
    filename_patterns: List[str]  # File patterns this profile applies to
    version: str = "1.0"
    author: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RedactionProfile':
        """Create profile from dictionary."""
        # Convert nested dictionaries back to dataclasses
        patterns = [RedactionRule(**p) if isinstance(p, dict) else p for p in data.get('patterns', [])]
        key_paths = [KeyPathRule(**k) if isinstance(k, dict) else k for k in data.get('key_paths', [])]
        
        return cls(
            name=data['name'],
            description=data['description'],
            log_format=LogFormat(data.get('log_format', 'plaintext')),
            patterns=patterns,
            key_paths=key_paths,
            entropy_config=data.get('entropy_config', {}),
            filename_patterns=data.get('filename_patterns', []),
            version=data.get('version', '1.0'),
            author=data.get('author')
        )


class ProfileManager:
    """Manages redaction profiles."""
    
    def __init__(self, profiles_dir: Optional[Union[str, Path]] = None):
        self.profiles_dir = Path(profiles_dir) if profiles_dir else Path(__file__).parent.parent / "profiles"
        self.profiles: Dict[str, RedactionProfile] = {}
        self._load_default_profiles()
    
    def _load_default_profiles(self):
        """Load built-in default profiles."""
        # Nginx access logs
        nginx_profile = RedactionProfile(
            name="nginx",
            description="Nginx access and error log redaction",
            log_format=LogFormat.PLAINTEXT,
            patterns=[
                RedactionRule(
                    pattern=r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
                    replacement='[REDACTED_IP]',
                    description="IP addresses"
                ),
                RedactionRule(
                    pattern=r'"[^"]*@[^"]*"',
                    replacement='"[REDACTED_EMAIL]"',
                    description="Email addresses in quotes"
                ),
                RedactionRule(
                    pattern=r'(password|pwd)=[^\s&]+',
                    replacement=r'\1=[REDACTED]',
                    description="Password parameters"
                )
            ],
            key_paths=[],
            entropy_config={
                "enabled": True,
                "threshold": 4.5,
                "min_length": 16
            },
            filename_patterns=["*.access.log", "*.error.log", "*nginx*.log"]
        )
        
        # Docker container logs
        docker_profile = RedactionProfile(
            name="docker",
            description="Docker container log redaction",
            log_format=LogFormat.JSON,
            patterns=[
                RedactionRule(
                    pattern=r'\b[A-Za-z0-9+/]{40,}={0,2}\b',
                    replacement='[REDACTED_TOKEN]',
                    description="Base64 tokens"
                ),
                RedactionRule(
                    pattern=r'(api[_-]?key|token|secret)[\s=:]+[^\s,}]+',
                    replacement=r'\1=[REDACTED]',
                    description="API keys and secrets"
                )
            ],
            key_paths=[
                KeyPathRule("env.*.password", "redact"),
                KeyPathRule("env.*.secret", "redact"),
                KeyPathRule("config.database.password", "redact"),
                KeyPathRule("labels.*.token", "redact")
            ],
            entropy_config={
                "enabled": True,
                "threshold": 4.2,
                "min_length": 12
            },
            filename_patterns=["*docker*.log", "container-*.log"]
        )
        
        # AWS CloudTrail
        cloudtrail_profile = RedactionProfile(
            name="cloudtrail",
            description="AWS CloudTrail log redaction",
            log_format=LogFormat.JSON,
            patterns=[
                RedactionRule(
                    pattern=r'\bAKIA[0-9A-Z]{16}\b',
                    replacement='[REDACTED_AWS_ACCESS_KEY]',
                    description="AWS access keys"
                ),
                RedactionRule(
                    pattern=r'\barn:aws:[^:]+:[^:]+:[0-9]{12}:',
                    replacement='arn:aws:service:region:[REDACTED_ACCOUNT]:',
                    description="AWS ARNs with account IDs"
                )
            ],
            key_paths=[
                KeyPathRule("userIdentity.accessKeyId", "redact"),
                KeyPathRule("responseElements.*.accessKeyId", "redact"),
                KeyPathRule("requestParameters.*.password", "redact"),
                KeyPathRule("sourceIPAddress", "redact")
            ],
            entropy_config={
                "enabled": True,
                "threshold": 4.0,
                "min_length": 20
            },
            filename_patterns=["*cloudtrail*.json", "*cloudtrail*.log"]
        )
        
        # Application logs (Rails, Django, etc.)
        application_profile = RedactionProfile(
            name="application",
            description="General application log redaction",
            log_format=LogFormat.PLAINTEXT,
            patterns=[
                RedactionRule(
                    pattern=r'(session[_-]?id|sessionid)[\s=:]+[^\s,}]+',
                    replacement=r'\1=[REDACTED_SESSION]',
                    description="Session IDs"
                ),
                RedactionRule(
                    pattern=r'(csrf[_-]?token|authenticity[_-]?token)[\s=:]+[^\s,}]+',
                    replacement=r'\1=[REDACTED_TOKEN]',
                    description="CSRF tokens"
                ),
                RedactionRule(
                    pattern=r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
                    replacement='[REDACTED_EMAIL]',
                    description="Email addresses"
                )
            ],
            key_paths=[],
            entropy_config={
                "enabled": True,
                "threshold": 4.2,
                "min_length": 12
            },
            filename_patterns=["*.application.log", "production.log", "*.rails.log"]
        )
        
        # Add all default profiles
        for profile in [nginx_profile, docker_profile, cloudtrail_profile, application_profile]:
            self.profiles[profile.name] = profile
    
    def load_profile_from_file(self, file_path: Union[str, Path]) -> RedactionProfile:
        """Load a profile from a JSON or YAML file."""
        file_path = Path(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        profile = RedactionProfile.from_dict(data)
        self.profiles[profile.name] = profile
        return profile
    
    def save_profile_to_file(self, profile: RedactionProfile, file_path: Union[str, Path]):
        """Save a profile to a JSON or YAML file."""
        file_path = Path(file_path)
        data = profile.to_dict()
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(data, f, default_flow_style=False, indent=2)
            else:
                json.dump(data, f, indent=2)
    
    def load_profiles_directory(self, directory: Union[str, Path]):
        """Load all profiles from a directory."""
        directory = Path(directory)
        
        if not directory.exists():
            return
        
        for file_path in directory.glob("*.json"):
            try:
                self.load_profile_from_file(file_path)
            except Exception as e:
                print(f"Error loading profile {file_path}: {e}")
        
        for file_path in directory.glob("*.yaml"):
            try:
                self.load_profile_from_file(file_path)
            except Exception as e:
                print(f"Error loading profile {file_path}: {e}")
    
    def get_profile(self, name: str) -> Optional[RedactionProfile]:
        """Get a profile by name."""
        return self.profiles.get(name)
    
    def list_profiles(self) -> List[str]:
        """List all available profile names."""
        return list(self.profiles.keys())
    
    def match_profile_for_file(self, file_path: Union[str, Path]) -> Optional[RedactionProfile]:
        """Find the best matching profile for a file based on filename patterns."""
        file_path = Path(file_path)
        filename = file_path.name.lower()
        
        for profile in self.profiles.values():
            for pattern in profile.filename_patterns:
                if self._matches_pattern(filename, pattern.lower()):
                    return profile
        
        return None
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a glob-like pattern."""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def create_custom_profile(self, 
                            name: str,
                            description: str,
                            patterns: List[RedactionRule],
                            log_format: LogFormat = LogFormat.PLAINTEXT,
                            key_paths: Optional[List[KeyPathRule]] = None,
                            entropy_config: Optional[Dict[str, Any]] = None,
                            filename_patterns: Optional[List[str]] = None) -> RedactionProfile:
        """Create a custom redaction profile."""
        profile = RedactionProfile(
            name=name,
            description=description,
            log_format=log_format,
            patterns=patterns,
            key_paths=key_paths or [],
            entropy_config=entropy_config or {"enabled": True, "threshold": 4.2, "min_length": 12},
            filename_patterns=filename_patterns or []
        )
        
        self.profiles[name] = profile
        return profile


def create_default_profiles_directory(output_dir: Union[str, Path]):
    """Create default profile files in the specified directory."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    manager = ProfileManager()
    
    for profile_name, profile in manager.profiles.items():
        output_file = output_dir / f"{profile_name}.json"
        manager.save_profile_to_file(profile, output_file)
        print(f"Created profile: {output_file}")


if __name__ == "__main__":
    # Test the profile system
    manager = ProfileManager()
    
    print("🔧 Available Profiles:")
    for name in manager.list_profiles():
        profile = manager.get_profile(name)
        print(f"  {name}: {profile.description}")
        print(f"    Format: {profile.log_format.value}")
        print(f"    Patterns: {len(profile.patterns)}")
        print(f"    Key Paths: {len(profile.key_paths)}")
        print()
    
    # Test file matching
    test_files = [
        "nginx.access.log",
        "app.production.log", 
        "cloudtrail-events.json",
        "container-app.log"
    ]
    
    print("🎯 Profile Matching:")
    for filename in test_files:
        matched = manager.match_profile_for_file(filename)
        profile_name = matched.name if matched else "No match"
        print(f"  {filename} -> {profile_name}")
