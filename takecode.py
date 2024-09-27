def run_python_code(file_path):
    # Read the content of the Python file dynamically
    with open(file_path, 'r') as file:
        code = file.read()
    
    # Use exec() to execute the code
    exec(code)


# Example of how to use it
if __name__ == "__main__":
    # You can pass the file path of the script to run (e.g., 'one.py')
    run_python_code('speakcount.py')
