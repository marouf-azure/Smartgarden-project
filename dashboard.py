import os
import json
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from dotenv import load_dotenv
from azure.storage.blob import ContainerClient

# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER")

# --------------------------------------------------
# 2. Configure Streamlit page
# --------------------------------------------------

st.set_page_config(
    page_title="Smart Garden Monitor",
    page_icon="🌱",
    layout="wide"
)
st_autorefresh(interval=10000, key="dashboard_refresh")
st.title("🌱 Smart Garden Monitor")
st.write("Monitoring sensor readings stored in Microsoft Azure.")

# --------------------------------------------------
# 3. Connect to Azure Blob Storage
# --------------------------------------------------

@st.cache_data(ttl=30)
def load_sensor_data():

    if not CONNECTION_STRING or not CONTAINER_NAME:
        raise ValueError("Azure Storage configuration is missing from .env")

    container_client = ContainerClient.from_connection_string(
        conn_str=CONNECTION_STRING,
        container_name=CONTAINER_NAME
    )

    readings = []

    # --------------------------------------------------
    # 4. Retrieve JSON files from Azure Blob Storage
    # --------------------------------------------------

    for blob in container_client.list_blobs():

        if not blob.name.lower().endswith(".json"):
            continue

        blob_client = container_client.get_blob_client(blob.name)

        content = blob_client.download_blob().readall()

        record = json.loads(content)

        if isinstance(record, list):
            readings.extend(record)
        elif isinstance(record, dict):
            readings.append(record)

    return pd.DataFrame(readings)

# --------------------------------------------------
# 5. Display sensor data
# --------------------------------------------------
try:
    with st.spinner("Connecting to Azure and retrieving sensor readings..."):
        df = load_sensor_data()

    if df.empty:
        st.warning("No sensor readings were found in the container.")

    else:
        st.success(f"Successfully retrieved {len(df)} sensor readings!")

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(
                df["timestamp"],
                errors="coerce",
                utc=True
            )

            df = df.sort_values("timestamp", ascending=False)

        latest = df.iloc[0]

        st.subheader("Latest Sensor Readings")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Soil Moisture",
                f"{latest['soilMoisture']}%"
                if "soilMoisture" in df.columns else "N/A"
            )

        with col2:
            st.metric(
                "Temperature",
                f"{latest['temperature']} °C"
                if "temperature" in df.columns else "N/A"
            )

        with col3:
            st.metric(
                "Sunlight",
                latest["sunlight"]
                if "sunlight" in df.columns else "N/A"
            )
                    # Low soil moisture warning
            if latest["soilMoisture"] < 30:
                st.error("🚨 LOW MOISTURE ALERT! Your plant needs water.")
            else:
                st.success("🌱 Soil moisture level is healthy.")
        # Sensor History Charts
        st.subheader("Sensor History Charts")

        chart_df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

        st.write("### Soil Moisture (%)")
        st.line_chart(
            chart_df.set_index("timestamp")["soilMoisture"]
        )

        st.write("### Temperature (°C)")
        st.line_chart(
            chart_df.set_index("timestamp")["temperature"]
        )

        st.write("### Sunlight")
        st.line_chart(
            chart_df.set_index("timestamp")["sunlight"]
        )

        # Complete Sensor Reading History
        st.subheader("Complete Sensor Reading History")
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("Unable to retrieve sensor readings from Azure.")
    st.exception(e)

# --------------------------------------------------
# 6. Sensor History Charts
# --------------------------------------------------

st.subheader("Sensor History Charts")

# Sort readings by timestamp for chronological charts
chart_df = df.sort_values("timestamp").copy()

# Soil Moisture Chart
st.write("### Soil Moisture (%)")

st.line_chart(
    chart_df.set_index("timestamp")["soilMoisture"]
)

# Temperature Chart
st.write("### Temperature (°C)")

st.line_chart(
    chart_df.set_index("timestamp")["temperature"]
)

# Sunlight Chart
st.write("### Sunlight")

st.line_chart(
    chart_df.set_index("timestamp")["sunlight"]
)

# --------------------------------------------------
# 7. Complete Sensor Reading History
# --------------------------------------------------

st.subheader("Complete Sensor Reading History")

st.dataframe(df, use_container_width=True)

