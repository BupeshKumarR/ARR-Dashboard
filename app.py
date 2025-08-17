from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Global variables for data
arr_summary = None
arr_rollforward = None
subscriptions = None

def load_data():
    """Load CSV data into global variables"""
    global arr_summary, arr_rollforward, subscriptions
    try:
        arr_summary = pd.read_csv('cleaned_arr_data/arr_monthly_summary.csv')
        arr_rollforward = pd.read_csv('cleaned_arr_data/arr_rollforward.csv')  
        subscriptions = pd.read_csv('cleaned_arr_data/subscriptions_clean.csv')
        print("✅ Data loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False

# Load data when app starts
load_data()

@app.route('/')
def dashboard():
    # Return your dashboard HTML
    with open('index.html', 'r') as f:
        html_content = f.read()
    return html_content

@app.route('/api/kpis')
def get_kpis():
    if arr_summary is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        latest = arr_summary.iloc[-1]
        previous = arr_summary.iloc[-2] if len(arr_summary) > 1 else latest
        
        return jsonify({
            'current_arr': float(latest['current_arr']),
            'active_customers': int(latest['active_customers']),
            'arr_per_customer': float(latest['current_arr'] / latest['active_customers']),
            'monthly_growth': float(latest['arr_growth_rate']) if pd.notna(latest['arr_growth_rate']) else 0,
            'arr_change': float(latest['current_arr'] - previous['current_arr']),
            'customer_change': int(latest['active_customers'] - previous['active_customers'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/waterfall')
def get_waterfall():
    if arr_rollforward is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        latest = arr_rollforward.iloc[-1]
        return jsonify({
            'month': latest['month'],
            'starting_arr': float(latest['starting_arr']),
            'new_arr': float(latest['new_arr']),
            'expansion_arr': float(latest['expansion_arr']),
            'contraction_arr': float(latest['contraction_arr']),
            'churned_arr': float(latest['churned_arr']),
            'ending_arr': float(latest['ending_arr'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trend')
def get_trend():
    recent_data = arr_summary.tail(12)
    trend_data = []
    
    for _, row in recent_data.iterrows():
        trend_data.append({
            'month': row['month'],
            'current_arr': float(row['current_arr']),
            'arr_growth_rate': float(row['arr_growth_rate']) if pd.notna(row['arr_growth_rate']) else 0,
            'active_customers': int(row['active_customers'])
        })
    
    return jsonify(trend_data)

@app.route('/api/segments')
def get_segments():
    active_subs = subscriptions[subscriptions['is_active'] == True]
    segment_data = active_subs.groupby('customer_segment').agg({
        'arr_amount': 'sum',
        'customer_id': 'count'
    }).reset_index()
    
    segments = []
    total_arr = segment_data['arr_amount'].sum()
    
    for _, row in segment_data.iterrows():
        segments.append({
            'segment': row['customer_segment'],
            'arr': float(row['arr_amount']),
            'customers': int(row['customer_id']),
            'percentage': float((row['arr_amount'] / total_arr) * 100) if total_arr > 0 else 0
        })
    
    return jsonify(segments)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=False)
