import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import pandas as pd  # Ensure you import pandas

# Customizing the layout
st.set_page_config(page_title="Stock Sense", page_icon="📈", layout="wide")

# Background color for the whole page
st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #F0F0F5;
    }
    .css-1d391kg {
        background-color: #0066CC;
        color: white;
    }
    .main {
        background-color: #F0F0F5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar logo for Yenepoya Institute in the upper left corner
logo_image = st.sidebar.file_uploader("Upload Yenepoya Institute logo", type=["jpg", "png"])

if logo_image:
    st.sidebar.image(logo_image, width=150, caption="Yenepoya Institute", use_column_width=False)
else:
    st.warning("Please upload the Yenepoya Institute logo.")

# Team Name and Project Title in the main content
st.markdown("<h1 style='text-align: center;'>Stock Sense</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>IBM Internship Project</h3>", unsafe_allow_html=True)

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

# Dictionary of popular stocks and their full names
stocks_dict = {
    "AAPL": "Apple Inc.",
    "GOOG": "Alphabet Inc. (Google)",
    "MSFT": "Microsoft Corporation",
    "AMZN": "Amazon.com Inc.",
    "TSLA": "Tesla Inc.",
    "META": "Meta Platforms Inc. (Facebook)",
    "NFLX": "Netflix Inc.",
    "NVDA": "Nvidia Corporation",
    "BABA": "Alibaba Group",
    "GME": "GameStop Corp.",
    "JNJ": "Johnson & Johnson",
    "WMT": "Walmart Inc.",
    "PG": "Procter & Gamble Co.",
    "V": "Visa Inc.",
    "JPM": "JPMorgan Chase & Co.",
    "DIS": "The Walt Disney Company",
    "AMD": "Advanced Micro Devices Inc.",
    "BA": "The Boeing Company",
    "KO": "The Coca-Cola Company",
    "PEP": "PepsiCo Inc."
}

# Create a list of formatted strings for the multiselect
stocks = [f"{symbol} - {name}" for symbol, name in stocks_dict.items()]

# Allow the user to select predefined stock symbols
selected_stocks = st.multiselect("Select stock symbols for prediction:", stocks, default=["AAPL - Apple Inc."])

# Allow the user to enter custom stock symbols
custom_stocks_input = st.text_input("Or, enter custom stock symbols (comma separated):", "")

# Combine predefined and custom stocks into a final list
if custom_stocks_input:
    custom_stocks = [symbol.strip().upper() for symbol in custom_stocks_input.split(",")]
    # Add the custom stocks to the selected stocks
    final_stocks = [stock.split(" - ")[0] for stock in selected_stocks] + custom_stocks
else:
    # Only use the predefined stocks if no custom input is provided
    final_stocks = [stock.split(" - ")[0] for stock in selected_stocks]

# Remove duplicates (if the same stock is selected both in predefined and custom inputs)
final_stocks = list(set(final_stocks))

# Proceed with the first stock for prediction (you can extend this to multiple stocks later)
if final_stocks:
    stock_to_predict = final_stocks[0]  # Taking the first stock for now
else:
    st.warning("Please select or enter at least one stock symbol.")
    st.stop()

n_year = st.slider("YEARS OF PREDICTION:", 1, 5)
period = n_year * 365

@st.cache_data
def load_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    return data

data_load_state = st.text("Loading data...")
data = load_data(stock_to_predict)
data_load_state.text("Loading data...done!")

# Plot the raw data
st.subheader('Raw data')
st.write(data.tail())

def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="Stock Close Price"))
    fig.layout.update(title_text='Time Series Data', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

plot_raw_data()

# Forecasting
df_train = data[['Date', 'Close']].copy()

# Ensure 'Close' column is numeric, dropping or filling NaN values
df_train['Close'] = pd.to_numeric(df_train['Close'], errors='coerce')
df_train = df_train.dropna(subset=['Close'])  # Remove rows where 'Close' is NaN

df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

m = Prophet()
m.fit(df_train)

future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

st.subheader('Forecast data')
st.write(forecast.tail())

st.write('Forecast plot')
fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)

st.write("Forecast components")
fig2 = m.plot_components(forecast)
st.write(fig2)
