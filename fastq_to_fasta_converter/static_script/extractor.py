import os

def fastq_to_fasta(file_path):
    file_name = os.path.splitext('file_path')[0]
    output_path = f"{file_name}.fasta"

    with open(file_path, 'r') as input_file, open(output_path, 'w') as output_file:
        for i, line in enumerate(input_file):
            if i%4 == 0:
                output_file.write('>' + line[1:])
            elif i%4 == 1:
                output_file.write(line)

    return output_path
