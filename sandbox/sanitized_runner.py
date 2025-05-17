import os
import sys
import signal
from textwrap import dedent
MAX_TIME = 5  # seconds

def execute_safely(code):
    # Get the original builtins safely
    original_builtins = {}
    try:
        import builtins
        original_builtins = builtins.__dict__
    except ImportError:
        original_builtins = __import__('__builtin__').__dict__

    # Create execution namespace with essential builtins
    execution_namespace = {
        '__builtins__': {
            'print': None,  # Will be replaced
            'range': range,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'super': super,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'enumerate': enumerate,
            'staticmethod': original_builtins.get('staticmethod'),
            'type': original_builtins.get('type'), 
            '__name__': '__main__'
        }
    }

    # Add __build_class__ if available
    if '__build_class__' in original_builtins:
        execution_namespace['__builtins__']['__build_class__'] = original_builtins['__build_class__']

    # Custom print handler
    output = []
    def custom_print(*args, **kwargs):
        end = kwargs.get('end', '\n')
        output.append(' '.join(str(arg) for arg in args)+end)
    
    try:
        # Normalize code indentation
        code = dedent(code)
        sys.setrecursionlimit(50)
        # Compile first for syntax checking
        compiled = compile(code, '<string>', 'exec')
        
        # Set timeout
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError))
        signal.alarm(MAX_TIME)
        
        # Replace print with our custom version
        execution_namespace['__builtins__']['print'] = custom_print
        
        # Execute with class support
        exec(compiled, execution_namespace, execution_namespace)
        
        return ''.join(output) if output else "Code executed successfully (no output)"
            
    except TimeoutError:
        return "Error: Execution timed out"
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"
    finally:
        signal.alarm(0)

if __name__ == '__main__':
    code = os.environ.get('PYTHON_CODE', '')
    print(execute_safely(code))