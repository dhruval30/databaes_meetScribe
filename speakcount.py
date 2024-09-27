from collections import Counter
import re
import matplotlib.pyplot as plt
from spacydata import get_text_data # Import the function to get text_data

# Call the function to get the text data
text_data = get_text_data()

# Custom logic to capture 'Speaker A', 'Speaker B', etc.
# Use regex to match the pattern "Speaker [A-Z]"
pattern = r"Speaker [A-Z]"
speakers = re.findall(pattern, get_text_data())

# Count the number of mentions for each speaker
speaker_counts = Counter(speakers)

# Print the counts of interactions per speaker
print("Speaker Interaction Counts:", speaker_counts)

# Extract speaker names and counts for the bar chart
speaker_names = list(speaker_counts.keys())
interaction_counts = list(speaker_counts.values())

# Create the bar chart
plt.bar(speaker_names, interaction_counts, color='blue')
plt.title("Speaker Interaction Amounts")
plt.xlabel("Speakers")
plt.ylabel("Number of Interactions")
plt.show()

