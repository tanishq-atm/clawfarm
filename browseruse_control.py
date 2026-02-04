#!/usr/bin/env python3
"""Quick Browser Use task control script"""
import sys
from browseruse_utils import BrowserUseClient, monitor_task

def show_usage():
    print("Usage: ./browseruse_control.py <command> [task_id]")
    print("\nCommands:")
    print("  current          - Show current Leonardo signup task status")
    print("  stop [task_id]   - Stop a task (defaults to current)")
    print("  monitor [task_id] - Monitor task until completion")
    print("  list             - List recent tasks")
    sys.exit(1)

def get_current_task_id():
    """Get task ID from leonardo_credentials.json"""
    try:
        import json
        with open('leonardo_credentials.json', 'r') as f:
            data = json.load(f)
            return data.get('task_id')
    except:
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        show_usage()
    
    command = sys.argv[1]
    client = BrowserUseClient()
    
    if command == "current":
        task_id = get_current_task_id()
        if not task_id:
            print("❌ No current task found in leonardo_credentials.json")
            sys.exit(1)
        
        print(f"📊 Current Leonardo signup task: {task_id}\n")
        task = client.get_task(task_id)
        
        print(f"Status: {task.get('status')}")
        print(f"Dashboard: https://cloud.browser-use.com/tasks/{task_id}")
        
        if task.get('output'):
            print(f"\nOutput:\n{task.get('output')}")
    
    elif command == "stop":
        if len(sys.argv) > 2:
            task_id = sys.argv[2]
        else:
            task_id = get_current_task_id()
        
        if not task_id:
            print("❌ No task ID provided and no current task found")
            sys.exit(1)
        
        print(f"🛑 Stopping task: {task_id}")
        result = client.stop_task(task_id)
        print(f"✅ Status: {result.get('status')}")
    
    elif command == "monitor":
        if len(sys.argv) > 2:
            task_id = sys.argv[2]
        else:
            task_id = get_current_task_id()
        
        if not task_id:
            print("❌ No task ID provided and no current task found")
            sys.exit(1)
        
        monitor_task(task_id, auto_stop=True)
    
    elif command == "list":
        tasks = client.list_tasks()
        print("Recent tasks:")
        for task in tasks.get('tasks', [])[:5]:
            print(f"  {task.get('id')} - {task.get('status')}")
    
    else:
        print(f"❌ Unknown command: {command}")
        show_usage()
