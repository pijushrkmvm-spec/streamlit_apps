import streamlit as st
import pandas as pd
import io

def reverse_complement(seq):
    seq = seq.lower()
    seq = seq.replace('a','T')
    seq = seq.replace('t','A')
    seq = seq.replace('g','C')
    seq = seq.replace('c','G')
    rev_seq = seq[::-1]
    rev_seq = rev_seq.upper()
    return rev_seq

def hairpin_loop(guide_seq, k=2):
    for i in range(len(guide_seq) - (2*k)):
        kmer = guide_seq[i:i+k]
        rc_kmer = reverse_complement(kmer)
        if rc_kmer in guide_seq[i+k+1:]:
            return True
    return False

def scoring_function(guide_seq):
    score = 100
    penalties = []

    # GC content
    gc_percent = ((guide_seq.count('G') + guide_seq.count('C')) / 20) * 100
    if gc_percent < 40:
        score -= (40 - gc_percent) * 1.5
        penalties.append("Low GC")
    elif gc_percent > 60:
        score -= (gc_percent - 60) * 1.5
        penalties.append("High GC")

    # gRNA position 20
    pos_20 = guide_seq[19]
    if pos_20 == "G":
        score += 5
    elif pos_20 == "C":
        score -= 10
        penalties.append("C at position 20")

    # Hairpin check
    if hairpin_loop(guide_seq):
        score -= 30
        penalties.append("Hairpin risk")

    # Scoring based status
    if score >= 90:
        status = "Excellent"
    elif score >= 70:
        status = f"Acceptable ({','.join(penalties)})"
    else:
        status = f"Poor ({','.join(penalties)})"

    return (score, gc_percent, status)

def sliding_window(dna_seq, strand='+'):
    seq = dna_seq.upper()
    results = []
    
    for i in range(len(seq)-22):
        window = seq[i:i+23]

        if window[21:23] == "GG":
            guide = window[:20]
            pam = window[20:23]

            if 'TTTT' in guide:
                continue

            score, gc, status = scoring_function(guide)

            results.append({
                "Guide (5' -> 3')": guide,
                "PAM": pam,
                "Strand": strand,
                "Position": i + 1, 
                "GC%": round(gc, 1),
                "Score": round(score, 1),
                "Status": status
            })
    return results

def crispr_predictor(forward_seq):
    """Expects a raw DNA string rather than a file path"""
    forward_seq = forward_seq.upper()
    reverse_seq = reverse_complement(forward_seq)

    forward_result = sliding_window(forward_seq, strand='+')
    reverse_result = sliding_window(reverse_seq, strand='-')

    all_results = forward_result + reverse_result
    df = pd.DataFrame(all_results)
    
    if not df.empty:
        df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
        
    return df

# streamlit app
st.set_page_config(page_title="CRISPR gRNA Designer", layout="wide")

st.title("CRISPR-Cas9 gRNA Designer")
st.write("Upload a target DNA sequence in FASTA format to predict and score potential SpCas9 guide RNAs.")

# About section
with st.expander("About the Scoring Logic", expanded=True):
    st.markdown("""
    This tool scans both the forward and reverse strands for `NGG` PAM motifs and evaluates the preceding 20bp guide sequence.
    * **Poly-T Exclusion:** Guides containing `TTTT` are dropped to prevent premature RNA transcription termination.
    * **GC Content:** Ideal GC content is 40-60%. Values outside this range receive scaled penalties.
    * **Seed Region:** A 'G' at position 20 boosts the score (+5), while a 'C' penalizes it (-10).
    * **Hairpin Check:** Penalizes sequences that form self-complementary secondary structures.
    """)

# Local app
with st.expander("Want to scan massive genomes locally?"):
    st.markdown("""
    You can get the standalone CLI script from the [GitHub repository](https://github.com/pijushrkmvm-spec/streamlit_apps/tree/main/grna_predictor).
    """)

# File Upload
uploaded_file = st.file_uploader("Upload Target Sequence (.fasta, .fa, .fna)", type=["fasta", "fa", "fna"])

if uploaded_file is not None:
    forward_seq = ""
    for line_bytes in uploaded_file:
        line = line_bytes.decode("utf-8").strip()
        if not line or line.startswith(">"):
            continue
        forward_seq += line

    if st.button("Predict gRNAs", type="primary"):
        if len(forward_seq) < 23:
            st.error("Sequence is too short! Must be at least 23 base pairs.")
        else:
            with st.spinner(f"Scanning {len(forward_seq)} base pairs for targets..."):
                result_df = crispr_predictor(forward_seq)

            if not result_df.empty:
                st.success(f"Successfully identified {len(result_df)} viable guide RNAs!")
                
                # Table
                st.dataframe(result_df, use_container_width=True, hide_index=True)
                
                # CSV Download Button
                csv_data = result_df.to_csv(index=False).encode('utf-8')
                
                # Extract file name
                base_name = uploaded_file.name.rsplit('.', 1)[0]
                output_name = f"{base_name}_gRNAs.csv"
                
                st.download_button(
                    label="Download Results (CSV)",
                    data=csv_data,
                    file_name=output_name,
                    mime="text/csv"
                )
            else:
                st.warning("No viable guide RNAs found in the uploaded sequence.")

st.markdown("---")
st.caption("© 2026 Pijush Chakraborty • Hosted on Streamlit")
