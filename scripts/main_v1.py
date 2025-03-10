import io
import pandas as pd
import streamlit as st

MAPPING = {
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


def transform_catalog(df: pd.DataFrame, marketplace: str) -> pd.DataFrame:
    """
    Transforms a marketplace catalog to LimeRoad's format.
    :param df: DataFrame containing the input file data
    :param marketplace: Marketplace name (e.g., 'myntra', 'ajio', 'flipkart')
    :return: Transformed DataFrame
    """
    transformed_data = pd.DataFrame()

    for lr_field, mapping in MAPPING.items():
        marketplace_field = mapping.get(marketplace)
        if marketplace_field in df.columns:
            transformed_data[lr_field] = df[marketplace_field]
        else:
            transformed_data[lr_field] = None

    return transformed_data


st.title("Marketplace Catalog Mapper")
st.write("Upload a marketplace catalog file to convert it to LimeRoad's format.")

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
marketplace = st.selectbox("Select Marketplace", ["myntra", "ajio", "flipkart"])

if uploaded_file and marketplace:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    transformed_df = transform_catalog(df, marketplace)

    output = io.BytesIO()
    transformed_df.to_csv(output, index=False)
    output.seek(0)

    st.success("Transformation complete! Download the file below.")
    st.download_button(
        "Download Transformed CSV", output, "transformed_catalog.csv", "text/csv"
    )
