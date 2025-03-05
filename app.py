import streamlit as st
import pandas as pd

# Streamlit App Title
st.title("Hotel Budget Mapper")

# File Uploaders
budget_file = st.file_uploader("Upload Budget File (XLSX)", type=["xlsx"])
template_file = st.file_uploader("Upload Template File (XLSX)", type=["xlsx"])

if budget_file and template_file:
    # Load data
    budget_df = pd.read_excel(budget_file)
    template_df = pd.read_excel(template_file)
    
    # Extract hotel name from template filename
    hotel_name = template_file.name.split("_")[0]  # Assuming format like 'ART_1_MAJOR_DAILY.xlsx'
    
    # Filter budget data for selected hotel
    filtered_df = budget_df[budget_df['HOTEL'] == hotel_name]
    
    # Convert 'GIORNO' to proper date format
    filtered_df['GIORNO'] = pd.to_datetime(filtered_df['GIORNO'], format='%d/%m/%y')
    
    # Aggregate RN and RR per segment and date
    aggregated_df = (
        filtered_df.groupby(['GIORNO', 'MKT_OPERA'])[['RN', 'RR']]
        .sum()
        .reset_index()
    )
    
    # Prepare output template
    output_df = template_df.copy()
    output_df.iloc[:, 0] = aggregated_df['GIORNO'].dt.strftime('%d/%m/%Y')
    
    # Map values to template columns
    for _, row in aggregated_df.iterrows():
        segment = row['MKT_OPERA']
        rn_col = f"{segment}_RN"
        rev_col = f"{segment}_REV"
        
        if rn_col in output_df.columns:
            output_df.loc[output_df.iloc[:, 0] == row['GIORNO'].strftime('%d/%m/%Y'), rn_col] = row['RN']
        if rev_col in output_df.columns:
            output_df.loc[output_df.iloc[:, 0] == row['GIORNO'].strftime('%d/%m/%Y'), rev_col] = row['RR']
    
    # Display results
    st.write("Mapped Data Preview:")
    st.dataframe(output_df)
    
    # Download button
    output_file = f"Mapped_{hotel_name}_Budget.xlsx"
    output_df.to_excel(output_file, index=False)
    st.download_button(
        label="Download Mapped Budget File",
        data=open(output_file, "rb"),
        file_name=output_file,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
