import streamlit as st
import pandas as pd
import io
import json
import os

st.set_page_config(page_title="LR Catalog Mapper", layout="wide")
st.markdown(
    """
    <style>
    .main {background-color: #f9f9f9; font-family: 'Segoe UI', sans-serif;}
    .css-1d391kg {padding: 1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("Instructions")
st.sidebar.info(
    """
1. Upload one or more CSV/Excel files with your marketplace catalog.
2. For each file, select the corresponding marketplace (Myntra, Flipkart, or Ajio).
3. Check the box if you want to proceed even if some expected headers are missing.
4. Click **Convert Files** to transform all catalogs into LR's format.
    """
)
st.sidebar.info(
    """
1. Review (and optionally edit) the mapping table below.
2. Save your mapping changes or reset to default using the buttons below.
    """
)

# Default mapping dictionary
DEFAULT_MAPPING = {
    "Brand Name": {"myntra": "brand", "ajio": "*Brand", "flipkart": "Brand"},
    "Color Grouping Code": {
        "myntra": "styleId",
        "ajio": "*Style Code",
        "flipkart": "Style Code",
    },
    "Vendor Style Code": {
        "myntra": "vendorSkuCode",
        "ajio": "*Item SKU",
        "flipkart": "Seller SKU ID",
    },
    "Size": {"myntra": "Standard Size", "ajio": "*Size", "flipkart": "Size"},
    "Color": {
        "myntra": "Brand Colour (Remarks)",
        "ajio": "*Primary Color",
        "flipkart": "Brand Color",
    },
    "Material": {"myntra": "Fabric", "ajio": "*Fabric Detail", "flipkart": "Fabric"},
    "MRP": {"myntra": "MRP", "ajio": "*MRP", "flipkart": "MRP"},
    "Selling Price": {
        "myntra": "Selling Price",
        "ajio": "Selling Price",
        "flipkart": "Selling Price",
    },
    "Stock / Inventory": {"myntra": "Stock Type", "ajio": "Stock Type", "flipkart": ""},
    "Print & Pattern": {
        "myntra": "Print or Pattern Type",
        "ajio": "*Pattern",
        "flipkart": "Pattern",
    },
    "Work": {"myntra": "Work", "ajio": "Work", "flipkart": ""},
    "Lining Material": {
        "myntra": "Lining Fabric",
        "ajio": "*Lining",
        "flipkart": "Lining Material",
    },
    "Sleeve Type": {
        "myntra": "Sleeve Styling",
        "ajio": "Sleeve Type",
        "flipkart": "Sleeve Style",
    },
    "Neck Type": {"myntra": "Neck", "ajio": "*Neckline", "flipkart": "Neck"},
    "Type": {"myntra": "Dress Shape", "ajio": "*Style Type", "flipkart": "Dress Type"},
    "Packed Width (inches)": {
        "myntra": "",
        "ajio": "*articleDimensionsUnitWidth",
        "flipkart": "packageDimensionsWidth",
    },
    "Packed Height (inches)": {
        "myntra": "",
        "ajio": "*articleDimensionsUnitHeight",
        "flipkart": "packageDimensionsHeight",
    },
    "Item Weight (kgs)": {
        "myntra": "",
        "ajio": "*articleDimensionsUnitWeight",
        "flipkart": "packageDimensionsWeight",
    },
    "Packed Length (inches)": {
        "myntra": "",
        "ajio": "*articleDimensionsUnitLength",
        "flipkart": "packageDimensionsLength",
    },
    "Pockets": {
        "myntra": "Number of Pockets",
        "ajio": "Number of Pockets",
        "flipkart": "",
    },
    "Care": {"myntra": "Wash Care", "ajio": "Care", "flipkart": "Fabric Care"},
    "Product Details": {
        "myntra": "Product Details",
        "ajio": "*Product Name",
        "flipkart": "Description",
    },
    "Image URL 1": {
        "myntra": "Front Image",
        "ajio": "*Main Image URL",
        "flipkart": "Main Image URL",
    },
    "Image URL 2": {
        "myntra": "Side Image",
        "ajio": "Other Image URL 1",
        "flipkart": "Other Image URL 1",
    },
    "Image URL 3": {
        "myntra": "Back Image",
        "ajio": "Other Image URL 2",
        "flipkart": "Other Image URL 2",
    },
    "Image URL 4": {
        "myntra": "Detail Angle",
        "ajio": "Other Image URL 3",
        "flipkart": "Other Image URL 3",
    },
    "Image URL 5": {
        "myntra": "Look Shot Image",
        "ajio": "Other Image URL 4",
        "flipkart": "Other Image URL 4",
    },
    "Transparency of Fabric": {
        "myntra": "Transparency",
        "ajio": "Transparency",
        "flipkart": "",
    },
    "Color Family": {
        "myntra": "Prominent Colour",
        "ajio": "*Color Family",
        "flipkart": "Color",
    },
    "Occasion": {"myntra": "Occasion", "ajio": "*Occasion", "flipkart": "Occasion"},
    "GST Rate": {"myntra": "", "ajio": "", "flipkart": ""},
    "HSN Code": {"myntra": "HSN", "ajio": "*HSN", "flipkart": "EAN/UPC"},
    "Closure": {"myntra": "Closure", "ajio": "Closure", "flipkart": ""},
    "Ideal for": {"myntra": "Ideal for", "ajio": "Ideal for", "flipkart": "Ideal For"},
    "GTIN": {"myntra": "GTIN", "ajio": "GTIN", "flipkart": "EAN/UPC"},
    "Manufacturing Date": {"myntra": "", "ajio": "", "flipkart": ""},
    "Country Of Origin": {
        "myntra": "Country Of Origin",
        "ajio": "*Country of Origin",
        "flipkart": "Country Of Origin",
    },
    "Fit": {"myntra": "", "ajio": "fit", "flipkart": ""},
    "Model Details": {"myntra": "", "ajio": "model details", "flipkart": ""},
}

mapping_file = "mapping.json"
if os.path.exists(mapping_file):
    with open(mapping_file, "r") as f:
        mapping_dict = json.load(f)
else:
    mapping_dict = DEFAULT_MAPPING.copy()


def transform_catalog(df: pd.DataFrame, marketplace: str) -> (pd.DataFrame, list):
    """
    Transforms a marketplace catalog to LR's format.
    Returns a tuple of (transformed DataFrame, list of missing expected header names).
    """
    transformed_data = pd.DataFrame()
    missing_headers = []

    for lr_field, mapping in mapping_dict.items():
        marketplace_field = mapping.get(marketplace)
        if marketplace_field:
            if marketplace_field in df.columns:
                transformed_data[lr_field] = df[marketplace_field]
            else:
                transformed_data[lr_field] = None
                missing_headers.append(marketplace_field)
        else:
            transformed_data[lr_field] = None

    return transformed_data, missing_headers


# MAIN APP UI
st.title("LR's Marketplace Catalog Mapper")
st.markdown("#")

# Display and edit mapping
st.subheader("Current Field Mapping (editable)")
mapping_df = pd.DataFrame.from_dict(mapping_dict, orient="index")
mapping_df.reset_index(inplace=True)
mapping_df.columns = ["limeroad", "myntra", "ajio", "flipkart"]
edited_mapping = st.data_editor(mapping_df, num_rows="dynamic", key="mapping_editor")

if not edited_mapping.empty:
    updated_mapping = {}
    for _, row in edited_mapping.iterrows():
        field = row["limeroad"]
        updated_mapping[field] = {
            "myntra": row["myntra"] if pd.notna(row["myntra"]) else "",
            "ajio": row["ajio"] if pd.notna(row["ajio"]) else "",
            "flipkart": row["flipkart"] if pd.notna(row["flipkart"]) else "",
        }
    mapping_dict = updated_mapping

col1, col2, col3 = st.columns([1, 2, 6])
with col1:
    if st.button("Save Mapping"):
        with open(mapping_file, "w") as f:
            json.dump(mapping_dict, f, indent=4)
        st.success("Mapping saved successfully!")
with col2:
    if st.button("Reset Mapping to Default"):
        mapping_dict = DEFAULT_MAPPING.copy()
        with open(mapping_file, "w") as f:
            json.dump(mapping_dict, f, indent=4)
        st.success("Mapping has been reset to default.")


st.markdown("#")
st.subheader("Upload marketplace catalog file(s) to convert to LR's format")

uploaded_files = st.file_uploader(
    "Upload CSV or Excel file(s)", type=["csv", "xlsx"], accept_multiple_files=True
)

file_marketplace = {}
if uploaded_files:
    st.markdown("### Select Marketplace for each file")
    for uploaded_file in uploaded_files:
        file_marketplace[uploaded_file.name] = st.selectbox(
            f"Marketplace for {uploaded_file.name}",
            ["myntra", "ajio", "flipkart"],
            key=uploaded_file.name,
        )

proceed_anyway = st.checkbox(
    "Proceed even if some expected headers are missing", value=False
)

if "all_outputs" not in st.session_state:
    st.session_state["all_outputs"] = []

if st.button("Convert Files"):
    if uploaded_files:
        all_outputs = []
        progress_bar = st.progress(0)
        total_files = len(uploaded_files)
        for idx, uploaded_file in enumerate(uploaded_files):
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file, dtype=str)
                else:
                    df = pd.read_excel(uploaded_file, dtype=str)

                marketplace = file_marketplace.get(uploaded_file.name, "")
                transformed_df, missing = transform_catalog(df, marketplace)

                if missing:
                    st.warning(
                        f"File {uploaded_file.name}: The following expected headers are missing: "
                        + ", ".join(missing)
                    )
                    if not proceed_anyway:
                        st.info(
                            "Please check your file headers or select the checkbox to proceed anyway."
                        )
                        continue
                output = io.BytesIO()
                transformed_df.to_csv(output, index=False)
                output.seek(0)
                all_outputs.append((uploaded_file.name, output))
                st.success(f"Processed {uploaded_file.name}.")
            except Exception as e:
                st.error(f"Failed to process {uploaded_file.name}: {e}")
            progress_bar.progress((idx + 1) / total_files)
        st.session_state["all_outputs"] = all_outputs
    else:
        st.info("Please upload at least one file.")

# download buttons for all processed files (persisted in session state)
if st.session_state["all_outputs"]:
    st.markdown("### Download Transformed Files")
    for file_name, output in st.session_state["all_outputs"]:
        st.download_button(
            f"Download Transformed {file_name}", output, f"LR_{file_name}", "text/csv"
        )
