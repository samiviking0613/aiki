#!/usr/bin/env python3
"""
🖥️ AIKI TERMINAL API
Python API for AIKI å kjøre terminal kommandoer

Usage:
    from src.aiki_terminal_api import AIKITerminal

    terminal = AIKITerminal()
    result = terminal.run("ps aux | grep python")

    if result["success"]:
        print(result["stdout"])

Created: 21. November 2025
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add aiki_terminal to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aiki_terminal import execute_command, ALLOWED_COMMANDS


class AIKITerminal:
    """
    Terminal API for AIKI

    Gir AIKI sikker tilgang til terminal kommandoer med:
    - Whitelist av tillatte kommandoer
    - Automatisk logging
    - Rate limiting
    """

    def __init__(self):
        self.command_history = []

    def run(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Kjør en terminal kommando

        Args:
            command: Bash kommando (må være whitelisted)
            timeout: Timeout i sekunder

        Returns:
            {
                "success": bool,
                "stdout": str,
                "stderr": str,
                "exit_code": int
            }
        """
        result = execute_command(command, timeout=timeout)
        self.command_history.append({
            "command": command,
            "success": result["success"]
        })
        return result

    def get_allowed_commands(self) -> list:
        """Få liste over tillatte kommandoer"""
        return list(ALLOWED_COMMANDS.keys())

    def diagnose_thread_explosion(self, process_name: str = None) -> Dict[str, Any]:
        """
        Diagnostiser thread explosion for en prosess

        Args:
            process_name: Prosess å sjekke (default: alle python prosesser)

        Returns:
            {
                "processes": [
                    {"pid": int, "name": str, "threads": int},
                    ...
                ],
                "total_threads": int,
                "anomalies": [str, ...]
            }
        """
        # Find Python processes
        if process_name:
            result = self.run(f"pgrep -f {process_name}")
        else:
            result = self.run("pgrep -f python")

        if not result["success"]:
            return {
                "processes": [],
                "total_threads": 0,
                "anomalies": ["Could not find processes"]
            }

        pids = result["stdout"].strip().split("\n")
        processes = []
        total_threads = 0
        anomalies = []

        for pid in pids:
            if not pid:
                continue

            # Count threads
            thread_result = self.run(f"ps -eLf | grep -E '^jovnna.*{pid}' | wc -l")
            if thread_result["success"]:
                thread_count = int(thread_result["stdout"].strip())

                # Get process info
                name_result = self.run(f"ps -p {pid} -o comm=")
                proc_name = name_result["stdout"].strip() if name_result["success"] else "unknown"

                processes.append({
                    "pid": int(pid),
                    "name": proc_name,
                    "threads": thread_count
                })

                total_threads += thread_count

                # Detect anomalies (more than 100 threads is suspicious)
                if thread_count > 100:
                    anomalies.append(f"PID {pid} ({proc_name}): {thread_count} threads (HØYT!)")

        return {
            "processes": processes,
            "total_threads": total_threads,
            "anomalies": anomalies
        }

    def fix_process_iter_bug(self, file_path: str) -> Dict[str, Any]:
        """
        Automatisk fix av psutil.process_iter() bug i en fil

        Args:
            file_path: Path til Python fil å fikse

        Returns:
            {
                "success": bool,
                "fixed": bool,
                "backup_path": str,
                "changes": int
            }
        """
        from pathlib import Path
        import shutil
        import re

        file_path = Path(file_path)

        if not file_path.exists():
            return {
                "success": False,
                "fixed": False,
                "error": f"File not found: {file_path}"
            }

        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + ".backup")
        shutil.copy(file_path, backup_path)

        # Read file
        content = file_path.read_text()

        # Pattern to replace
        pattern = r"for\s+(\w+)\s+in\s+psutil\.process_iter\((.*?)\):"
        replacement = r"# FIXED: Use psutil.pids() to avoid thread explosion\nfor pid in psutil.pids():\n    try:\n        \1 = psutil.Process(pid)"

        # Count matches
        matches = len(re.findall(pattern, content))

        if matches == 0:
            return {
                "success": True,
                "fixed": False,
                "message": "No psutil.process_iter() found",
                "backup_path": str(backup_path)
            }

        # Replace
        new_content = re.sub(pattern, replacement, content)

        # Write back
        file_path.write_text(new_content)

        return {
            "success": True,
            "fixed": True,
            "backup_path": str(backup_path),
            "changes": matches,
            "message": f"Fixed {matches} occurrences of process_iter()"
        }


# Example usage
if __name__ == "__main__":
    terminal = AIKITerminal()

    print("🖥️ AIKI TERMINAL API - TEST\n")

    # Test 1: List Python processes
    print("TEST 1: List Python processes")
    result = terminal.run("ps aux | grep python | head -5")
    if result["success"]:
        print(result["stdout"])

    # Test 2: Thread explosion diagnosis
    print("\nTEST 2: Diagnose thread explosion")
    diagnosis = terminal.diagnose_thread_explosion()
    print(f"Total threads: {diagnosis['total_threads']}")
    print(f"Anomalies: {len(diagnosis['anomalies'])}")
    for anomaly in diagnosis["anomalies"]:
        print(f"  - {anomaly}")

    # Test 3: List allowed commands
    print("\nTEST 3: Allowed commands")
    print(terminal.get_allowed_commands())
