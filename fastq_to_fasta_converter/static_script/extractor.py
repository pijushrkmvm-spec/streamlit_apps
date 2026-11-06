# Import required libraries
import os

path = input("Enter the path of the file: ")
# Define the function for the converter
def fastq_to_fasta(file_path):
    # Extracting the name from the .fastq file
    file_name = os.path.splitext(file_path)[0]
    # Defining the output file name
    output_path = f"{file_name}.fasta"

    # Opening the .fastq file and creating output file function
    with open(file_path, 'r') as input_file, open(output_path, 'w') as output_file:
        # Core function for the extraction
        for i, line in enumerate(input_file):
            if i%4 == 0:
                output_file.write('>' + line[1:])
            elif i%4 == 1:
                output_file.write(line)

    return output_path

# Calling the function
fastq_to_fasta(path)
