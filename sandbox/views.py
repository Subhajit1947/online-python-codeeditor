from django.shortcuts import render
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
# from .models import CodeExecution
import docker
import re

client = docker.from_env()


def editor(request):
    return render(request,'editor.html')



@ratelimit(key='ip', rate='5/m')
def execute_code(request):
    if request.method == 'POST':
        code = request.POST.get('code', '')
        # Security checks
        if not is_code_safe(code):
            return JsonResponse({'error': 'Dangerous code detected'}, status=400)
        
        # Execute in container
        try:
            result = client.containers.run(
                'python-sandbox',
                command=f"python sanitized_runner.py",
                environment={'PYTHON_CODE': code},
                mem_limit='100m',
                network_mode='none',
                remove=True
            ).decode()
            if result.split(':')[0].lower()=='error':
                return JsonResponse({'error': result})
            return JsonResponse({'output': result})
            
        except docker.errors.ContainerError as e:
            return JsonResponse({
                'error': 'Execution error',
                'details': e.stderr.decode() if e.stderr else str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def is_code_safe(code):
    """Validate Python code using AST and regex"""
    blacklist = [
        r'__import__\s*\(',
        r'eval\s*\(',
        r'exec\s*\(',
        r'open\s*\(',
        r'os\.',
        r'subprocess\.',
        r'import\s+os',
        r'import\s+subprocess'
    ]
    
    if any(re.search(pattern, code) for pattern in blacklist):
        return False
        
    try:
        import ast
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ['os', 'subprocess', 'sys', 'socket']:
                        return False
            elif isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and node.func.id in ['eval', 'exec']:
                    return False
    except:
        return False
        
    return True