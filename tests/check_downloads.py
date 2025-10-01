#!/usr/bin/env python3
"""
Check Downloads and Model Storage
Shows where models and data are stored to avoid duplication
"""

import os
import sys
from pathlib import Path

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "info": "\033[32m✅",      # Green
        "warn": "\033[33m⚠️ ",     # Yellow
        "error": "\033[31m❌",     # Red
        "header": "\033[36m📁",    # Cyan
        "size": "\033[35m📊",      # Magenta
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')} {message}{reset}")

def get_dir_size(path):
    """Get directory size in MB"""
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size / (1024 * 1024)  # Convert to MB
    except:
        return 0

def check_whisper_cache():
    """Check Whisper model cache"""
    print_status("Whisper Model Cache", "header")

    # Whisper stores models in ~/.cache/whisper
    whisper_cache = Path.home() / ".cache" / "whisper"

    if whisper_cache.exists():
        models = list(whisper_cache.glob("*.pt"))
        total_size = get_dir_size(whisper_cache)

        print_status(f"Location: {whisper_cache}", "info")
        print_status(f"Total size: {total_size:.1f} MB", "size")

        if models:
            for model in models:
                model_size = model.stat().st_size / (1024 * 1024)
                print_status(f"  {model.name}: {model_size:.1f} MB", "info")
        else:
            print_status("  No Whisper models downloaded yet", "warn")
    else:
        print_status("No Whisper cache found", "warn")

    print()

def check_huggingface_cache():
    """Check Hugging Face model cache"""
    print_status("Hugging Face Model Cache", "header")

    # HF stores models in ~/.cache/huggingface
    hf_cache = Path.home() / ".cache" / "huggingface"

    if hf_cache.exists():
        hub_cache = hf_cache / "hub"
        total_size = get_dir_size(hf_cache)

        print_status(f"Location: {hf_cache}", "info")
        print_status(f"Total size: {total_size:.1f} MB", "size")

        if hub_cache.exists():
            # List model repos
            repos = [d for d in hub_cache.iterdir() if d.is_dir() and d.name.startswith("models--")]

            if repos:
                print_status(f"Found {len(repos)} model repositories:", "info")
                for repo in repos[:10]:  # Show first 10
                    repo_name = repo.name.replace("models--", "").replace("--", "/")
                    repo_size = get_dir_size(repo)
                    print_status(f"  {repo_name}: {repo_size:.1f} MB", "info")

                if len(repos) > 10:
                    print_status(f"  ... and {len(repos) - 10} more", "info")
            else:
                print_status("  No HuggingFace models downloaded yet", "warn")
    else:
        print_status("No HuggingFace cache found", "warn")

    print()

def check_local_models():
    """Check local models directory"""
    print_status("Local Models Directory", "header")

    models_dir = Path("models")

    if models_dir.exists():
        total_size = get_dir_size(models_dir)
        print_status(f"Location: {models_dir.absolute()}", "info")
        print_status(f"Total size: {total_size:.1f} MB", "size")

        # List contents
        contents = list(models_dir.iterdir())
        if contents:
            for item in contents:
                if item.is_file():
                    size = item.stat().st_size / (1024 * 1024)
                    print_status(f"  {item.name}: {size:.1f} MB", "info")
                elif item.is_dir():
                    dir_size = get_dir_size(item)
                    print_status(f"  {item.name}/: {dir_size:.1f} MB", "info")
        else:
            print_status("  Directory is empty", "warn")
    else:
        print_status("Local models directory doesn't exist", "warn")

    print()

def check_data_directories():
    """Check data storage directories"""
    print_status("Data Storage Directories", "header")

    data_dirs = [
        ("data", "Main data directory"),
        ("data/recordings", "Audio recordings"),
        ("data/meetings", "Meeting data"),
        ("data/temp", "Temporary files"),
        ("test_data", "Test files"),
    ]

    for dir_path, description in data_dirs:
        path = Path(dir_path)
        if path.exists():
            size = get_dir_size(path)
            file_count = len(list(path.rglob("*"))) if path.is_dir() else 0
            print_status(f"{description}: {path.absolute()}", "info")
            print_status(f"  Size: {size:.1f} MB, Files: {file_count}", "size")
        else:
            print_status(f"{description}: Not created yet", "warn")

    print()

def check_ollama_models():
    """Check Ollama model storage"""
    print_status("Ollama Model Storage", "header")

    # Ollama typically stores models in ~/.ollama
    ollama_dir = Path.home() / ".ollama"

    if ollama_dir.exists():
        models_dir = ollama_dir / "models"
        total_size = get_dir_size(ollama_dir)

        print_status(f"Location: {ollama_dir}", "info")
        print_status(f"Total size: {total_size:.1f} MB", "size")

        if models_dir.exists():
            # Try to list models via ollama command
            try:
                import subprocess
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    if lines and lines[0]:
                        print_status("Downloaded models:", "info")
                        for line in lines:
                            if line.strip():
                                parts = line.split()
                                if len(parts) >= 3:
                                    name, tag, size = parts[0], parts[1], parts[2]
                                    print_status(f"  {name}:{tag} - {size}", "info")
                    else:
                        print_status("  No Ollama models downloaded yet", "warn")
                else:
                    print_status("  Could not list Ollama models", "warn")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                print_status("  Ollama command not available", "warn")
    else:
        print_status("No Ollama installation found", "warn")

    print()

def check_system_cache():
    """Check system-wide cache usage"""
    print_status("System Cache Summary", "header")

    cache_dirs = [
        (Path.home() / ".cache", "User cache"),
        (Path("/tmp"), "Temporary files"),
        (Path.home() / ".local" / "share", "Local data"),
    ]

    total_cache_size = 0

    for cache_path, description in cache_dirs:
        if cache_path.exists():
            size = get_dir_size(cache_path)
            total_cache_size += size
            print_status(f"{description}: {size:.1f} MB", "size")

    print_status(f"Total cache usage: {total_cache_size:.1f} MB", "size")
    print()

def show_cleanup_commands():
    """Show commands to clean up downloads"""
    print_status("Cleanup Commands (if needed)", "header")

    print("To free up space, you can remove:")
    print()
    print("  # Clear Whisper models")
    print("  rm -rf ~/.cache/whisper")
    print()
    print("  # Clear HuggingFace models")
    print("  rm -rf ~/.cache/huggingface")
    print()
    print("  # Clear local models")
    print("  rm -rf ./models")
    print()
    print("  # Clear Ollama models")
    print("  ollama rm <model_name>  # Remove specific model")
    print("  # or")
    print("  rm -rf ~/.ollama")
    print()
    print("  # Clear meeting data")
    print("  rm -rf ./data/meetings")
    print("  rm -rf ./data/recordings")
    print()

def main():
    """Main function"""
    print("=" * 70)
    print("📁 MEETING ASSISTANT - DOWNLOAD LOCATIONS")
    print("=" * 70)
    print("This shows where models and data are stored to avoid duplication")
    print()

    check_whisper_cache()
    check_huggingface_cache()
    check_local_models()
    check_ollama_models()
    check_data_directories()
    check_system_cache()
    show_cleanup_commands()

    print("=" * 70)
    print("💡 TIPS TO AVOID DUPLICATION:")
    print("=" * 70)
    print("1. Whisper models are cached globally (~/.cache/whisper)")
    print("2. HuggingFace models are cached globally (~/.cache/huggingface)")
    print("3. Ollama models are stored globally (~/.ollama)")
    print("4. Only meeting data is stored locally (./data/)")
    print("5. Multiple projects can share the same model caches")
    print()
    print("Run this script anytime to check storage usage!")

if __name__ == "__main__":
    main()