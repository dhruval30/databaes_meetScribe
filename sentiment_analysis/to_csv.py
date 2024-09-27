import csv

def parse_transcript(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    parsed_data = []

    for line in lines:
        if ': ' in line:
            speaker, dialogue = line.split(': ', 1)
            parsed_data.append([speaker.strip(), dialogue.strip()])
    
    return parsed_data

def write_to_csv(parsed_data, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Speaker', 'Dialogue'])
        writer.writerows(parsed_data)

input_file = 'sentiment_analysis/diarized_text.txt'
output_file = 'sentiment_analysis/diarized_text.csv'

parsed_data = parse_transcript(input_file)
write_to_csv(parsed_data, output_file)

print(f'Transcript saved to {output_file}')

