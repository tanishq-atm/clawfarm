#!/usr/bin/env python3
"""Browser Use API utilities for task control"""
import os
import json
import time
from typing import Optional, Dict
from dotenv import load_dotenv
import httpx

load_dotenv()

class BrowserUseClient:
    """Browser Use API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BROWSERUSE_API_KEY", "bu_RE73gaEVWynxZNuRjWlyLxQWQTFz2-8vwQNBFdhtauw")
        self.base_url = "https://api.browser-use.com/api/v2"
        self.headers = {"X-Browser-Use-API-Key": self.api_key}
    
    def create_session(self, profile_id: Optional[str] = None) -> Dict:
        """Create a new browser session"""
        payload = {}
        if profile_id:
            payload["profileId"] = profile_id
        
        response = httpx.post(
            f"{self.base_url}/sessions",
            headers=self.headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def stop_session(self, session_id: str) -> Dict:
        """Stop a browser session"""
        response = httpx.post(
            f"{self.base_url}/sessions/{session_id}/stop",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_session(self, session_id: str) -> Dict:
        """Get session details"""
        response = httpx.get(
            f"{self.base_url}/sessions/{session_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_task(
        self, 
        task: str, 
        llm: str = "browser-use-llm",
        start_url: Optional[str] = None,
        max_steps: int = 100,
        session_id: Optional[str] = None
    ) -> Dict:
        """Create a new browser automation task"""
        payload = {
            "task": task,
            "llm": llm,
            "maxSteps": max_steps
        }
        
        if start_url:
            payload["startUrl"] = start_url
        if session_id:
            payload["sessionId"] = session_id
        
        response = httpx.post(
            f"{self.base_url}/tasks",
            headers=self.headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def get_task(self, task_id: str) -> Dict:
        """Get task status and details"""
        response = httpx.get(
            f"{self.base_url}/tasks/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def stop_task(self, task_id: str) -> Dict:
        """Stop a running task"""
        response = httpx.patch(
            f"{self.base_url}/tasks/{task_id}",
            headers=self.headers,
            json={"status": "stopped"}
        )
        response.raise_for_status()
        return response.json()
    
    def list_tasks(self, limit: int = 10) -> Dict:
        """List recent tasks"""
        response = httpx.get(
            f"{self.base_url}/tasks",
            headers=self.headers,
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(
        self, 
        task_id: str, 
        timeout_seconds: int = 600,
        poll_interval: int = 15,
        verbose: bool = True
    ) -> Dict:
        """
        Poll task until completion or timeout
        
        Args:
            task_id: Task ID to monitor
            timeout_seconds: Max time to wait (default 10 min)
            poll_interval: Seconds between checks (default 15s)
            verbose: Print status updates
        
        Returns:
            Final task dict
        """
        max_attempts = timeout_seconds // poll_interval
        
        if verbose:
            print(f"⏳ Waiting for task {task_id}")
            print(f"   Timeout: {timeout_seconds}s\n")
        
        for attempt in range(1, max_attempts + 1):
            try:
                task = self.get_task(task_id)
                status = task.get("status")
                
                if verbose:
                    print(f"   [{attempt}/{max_attempts}] Status: {status}")
                
                # Terminal states
                if status in ["finished", "failed", "stopped"]:
                    if verbose:
                        print(f"\n✅ Task completed with status: {status}\n")
                    return task
                
                time.sleep(poll_interval)
            
            except Exception as e:
                if verbose:
                    print(f"   ❌ Error checking status: {e}")
                time.sleep(poll_interval)
        
        if verbose:
            print(f"\n⏱️ Timeout after {timeout_seconds}s")
        
        # Return last known state
        try:
            return self.get_task(task_id)
        except:
            return {"status": "timeout", "id": task_id}
    
    def get_task_output(self, task_id: str) -> Optional[str]:
        """Get the output/result from a completed task"""
        task = self.get_task(task_id)
        return task.get("output")
    
    def is_task_running(self, task_id: str) -> bool:
        """Check if task is still running"""
        task = self.get_task(task_id)
        status = task.get("status")
        return status in ["pending", "started", "running"]


def monitor_task(task_id: str, auto_stop: bool = False):
    """
    Interactive task monitor - prints status updates
    
    Args:
        task_id: Task to monitor
        auto_stop: If True, offers to stop if user presses Ctrl+C
    """
    client = BrowserUseClient()
    
    print(f"📊 Monitoring task: {task_id}")
    print(f"   Dashboard: https://cloud.browser-use.com/tasks/{task_id}")
    if auto_stop:
        print(f"   Press Ctrl+C to stop task\n")
    else:
        print()
    
    try:
        result = client.wait_for_completion(task_id, verbose=True)
        
        print("\n" + "="*60)
        print("TASK RESULT")
        print("="*60)
        print(f"Status: {result.get('status')}")
        print(f"Success: {result.get('isSuccess')}")
        
        output = result.get('output')
        if output:
            print(f"\nOutput:\n{output}\n")
        
        cost = result.get('cost')
        if cost:
            print(f"Cost: ${cost}")
        
        return result
    
    except KeyboardInterrupt:
        if auto_stop:
            print("\n\n⚠️  Interrupt detected. Stop task? (y/n): ", end="")
            response = input().strip().lower()
            if response == 'y':
                print(f"🛑 Stopping task {task_id}...")
                client.stop_task(task_id)
                print("✅ Task stopped")
            else:
                print("Task continues running in background")
        else:
            print("\n\n⚠️  Monitor interrupted (task still running)")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python browseruse_utils.py <command> [args]")
        print("\nCommands:")
        print("  status <task_id>     - Check task status")
        print("  stop <task_id>       - Stop a running task")
        print("  monitor <task_id>    - Monitor task until completion")
        print("  list                 - List recent tasks")
        sys.exit(1)
    
    command = sys.argv[1]
    client = BrowserUseClient()
    
    if command == "status":
        task_id = sys.argv[2]
        result = client.get_task(task_id)
        print(json.dumps(result, indent=2))
    
    elif command == "stop":
        task_id = sys.argv[2]
        print(f"🛑 Stopping task {task_id}...")
        result = client.stop_task(task_id)
        print(f"✅ {result.get('status')}")
    
    elif command == "monitor":
        task_id = sys.argv[2]
        monitor_task(task_id, auto_stop=True)
    
    elif command == "list":
        result = client.list_tasks()
        print(json.dumps(result, indent=2))
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
