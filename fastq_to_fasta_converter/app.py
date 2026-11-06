import io
import streamlit as st

# Page title and basic layout
st.set_page_config(page_title="FASTQ to FASTA Converter")

st.title("FASTQ to FASTA Converter")
st.subheader("Developed for Ramakrishna Mission Vidyamandira - Department of Microbiology")
st.write("Upload a FASTQ file to convert and extract sequences into FASTA format.")

# About section
with st.expander("About & How to Use", expanded=False):
    st.markdown("""
    ### How to Use
    1. **Upload your FASTQ file** (`.fastq` or `.fq`) using the file uploader below (Maximum file size 500MB per file).
    2. Click **Convert to FASTA** to begin line-by-line sequence parsing.
    3. Click **Download FASTA File** once processing finishes to retrieve your file.

    ---

    ### Want to convert larger fastq file?
    You can get the converter function from the GitHub['https://github.com/pijushrkmvm-spec/streamlit_apps/edit/main/fastq_to_fasta_converter/static_script'] repository.
    You can clone the script into your local machine and run it from the folder where you kept the fastq file
    Please keep in mind it will use RAM from your local machine, please select the input file cautiously

    ---

    ### Scientific Note: Multi-FASTA Output
    This tool outputs a **Multi-FASTA** format file where each sequence record is preserved with its corresponding original read identifier from the FASTQ header (`>Header`).

    * **Preserving Read Identity:** Every raw sequencing read represents an independent biological fragment or single transcript. Retaining individual read headers is critical for preserving variant information and read boundaries.
    * **Downstream Compatibility:** Most bioinformatic software (e.g., BLAST, BWA, Bowtie2, Minimap2, spades) expects multi-record FASTA format when aligning, assembling, or quantifying high-throughput sequencing data.
    * **Quality Score Removal:** FASTQ quality scores (Phred lines) are stripped out to generate a lightweight, sequence-only FASTA payload.
    """)

# File Uploader
uploaded_file = st.file_uploader("Choose a FASTQ file", type=["fastq", "fq"])

if uploaded_file is not None:
    original_name = uploaded_file.name
    if '.' in original_name:
        base_name = original_name.rsplit('.', 1)[0]
    else:
        base_name = original_name
    output_filename = f"{base_name}.fasta"

    # submit button
    if st.button("Convert to FASTA", type="primary"):
        with st.spinner("Converting sequences..."):
            fasta_buffer = io.StringIO()

            
            for i, line_bytes in enumerate(uploaded_file):
                line = line_bytes.decode('utf-8', errors='ignore')
                if i % 4 == 0:
                    fasta_buffer.write('>' + line[1:])
                elif i % 4 == 1:
                    fasta_buffer.write(line)

            fasta_data = fasta_buffer.getvalue()
            fasta_buffer.close()

        st.success("Conversion complete!")

        # FASTA download
        st.download_button(
            label="Download FASTA File",
            data=fasta_data,
            file_name=output_filename,
            mime="text/plain"
        )

st.markdown("---")
st.caption("© 2026 Pijush Chakraborty • Hosted on Streamlit")
