import pandas as pd
import os
import tabulate

def reverse_complement(seq):
    seq = seq.lower()
    seq = seq.replace('a','T')
    seq = seq.replace('t','A')
    seq = seq.replace('g','C')
    seq = seq.replace('c','G')
    rev_seq = seq[::-1]
    rev_seq = rev_seq.upper()
    return rev_seq

def hairpin_loop(guide_seq, k = 2):
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
    gc_percent = ((guide_seq.count('G')+guide_seq.count('C'))/20)*100
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
        status = f"Acceptable, ({','.join(penalties)})"
    else:
        status = f"Poor, ({','.join(penalties)})"

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
                "Position": i + 1, # 1-based biological indexing
                "GC%": round(gc, 1),
                "Score": round(score, 1),
                "Status": status
            })
    return results

def crispr_predictor(file_path):
    forward_seq = ""
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith('>'):
                continue

            forward_seq += line

    forward_seq = forward_seq.upper()
    reverse_seq = reverse_complement(forward_seq)

    forward_result = sliding_window(forward_seq, strand='+')
    reverse_result = sliding_window(reverse_seq, strand='-')

    all_results = forward_result + reverse_result
    df = pd.DataFrame(all_results)
    
    if not df.empty:
        df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
        
    return df


# Calling the function
file_to_test = input("Enter file path: ")
print(f"Analyzing {file_to_test}...")
result_df = crispr_predictor(file_to_test)
    
if not result_df.empty:
    # Print the results to the terminal
    print("\n--- CRISPR gRNA Predictions ---")
    print(result_df.to_markdown(index=False))
    
    # Save the results to a CSV file so you can open it in Excel
    output_csv = "predicted_guides.csv"
    result_df.to_csv(output_csv, index=False)
    print(f"\n Results successfully saved to {output_csv}")
else:
    print("\n No viable guide RNAs found in this sequence.")
