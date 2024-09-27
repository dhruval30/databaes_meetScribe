import subprocess

# Define the path to the script you want to run
script_path = 'speakcount.py'

# Run the script using subprocess
try:
    result = subprocess.run(['python', script_path], capture_output=True, text=True)

    # Print the output from the script (both stdout and stderr)
    print("Output from speaker_analysis.py:")
    print(result.stdout)

    # If there are errors, print them
    if result.stderr:
        print("Errors:")
        print(result.stderr)

except Exception as e:
    print(f"An error occurred: {e}")
