import io
import streamlit as st

# Page title and basic layout
st.set_page_config(page_title="FASTQ to FASTA Converter")

st.title("FASTQ to FASTA Converter")
st.subheader("Developed for Ramakrishna Mission Vidyamandira - Department of Microbiology")
st.write("Upload a FASTQ file to convert and extract sequences into FASTA format.")

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
