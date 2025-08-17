"""
Complete SaaS ARR Data Engineering Pipeline
Run this script locally on your Mac to process ARR data

Prerequisites:
pip install pandas numpy openpyxl

Usage:
1. Download CSV files from the data generator 
2. Place them in same folder as this script
3. Run: python saas_data_engineering.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def step1_data_ingestion():
    """
    Load and inspect CSV files
    """
    print("🔄 STEP 1: DATA INGESTION")
    print("=" * 50)
    
    # Check if CSV files exist
    required_files = ['saas_customers.csv', 'saas_subscriptions.csv', 'saas_transactions.csv']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        print("💡 Please download CSV files from the data generator first!")
        return None, None, None
    
    try:
        # Load CSV files
        customers_df = pd.read_csv('saas_customers.csv')
        subscriptions_df = pd.read_csv('saas_subscriptions.csv')
        transactions_df = pd.read_csv('saas_transactions.csv')
        
        print(f"✅ Loaded {len(customers_df):,} customers")
        print(f"✅ Loaded {len(subscriptions_df):,} subscriptions") 
        print(f"✅ Loaded {len(transactions_df):,} transactions")
        
        # Basic data overview
        print(f"\n📊 Data Overview:")
        print(f"Date range: {transactions_df['transaction_date'].min()} to {transactions_df['transaction_date'].max()}")
        print(f"Unique customers: {customers_df['customer_id'].nunique():,}")
        print(f"Transaction types: {list(transactions_df['transaction_type'].unique())}")
        
        return customers_df, subscriptions_df, transactions_df
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None, None, None

def step2_data_cleaning(customers_df, subscriptions_df, transactions_df):
    """
    Clean and standardize all datasets
    """
    print("\n🧹 STEP 2: DATA CLEANING")
    print("=" * 50)
    
    # Clean customers data
    print("Cleaning customers data...")
    customers_df['signup_date'] = pd.to_datetime(customers_df['signup_date'])
    customers_df['company_name'] = customers_df['company_name'].str.strip()
    
    # Clean subscriptions data  
    print("Cleaning subscriptions data...")
    subscriptions_df['start_date'] = pd.to_datetime(subscriptions_df['start_date'])
    subscriptions_df['end_date'] = pd.to_datetime(subscriptions_df['end_date'])
    subscriptions_df['mrr_amount'] = pd.to_numeric(subscriptions_df['mrr_amount'], errors='coerce')
    subscriptions_df['arr_amount'] = pd.to_numeric(subscriptions_df['arr_amount'], errors='coerce')
    
    # Clean transactions data
    print("Cleaning transactions data...")
    transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
    transactions_df['amount'] = pd.to_numeric(transactions_df['amount'], errors='coerce')
    
    # Remove invalid records
    before_cleaning = len(transactions_df)
    transactions_df = transactions_df.dropna(subset=['transaction_date', 'amount'])
    after_cleaning = len(transactions_df)
    
    print(f"✅ Cleaned data - removed {before_cleaning - after_cleaning} invalid records")
    
    # Data quality report
    print(f"\n📋 Data Quality Report:")
    print(f"Missing customer signup dates: {customers_df['signup_date'].isna().sum()}")
    print(f"Missing subscription amounts: {subscriptions_df['mrr_amount'].isna().sum()}")
    print(f"Missing transaction amounts: {transactions_df['amount'].isna().sum()}")
    
    return customers_df, subscriptions_df, transactions_df

def step3_feature_engineering(customers_df, subscriptions_df, transactions_df):
    """
    Create calculated fields and derived features
    """
    print("\n⚙️ STEP 3: FEATURE ENGINEERING")
    print("=" * 50)
    
    # Add time-based features
    print("Creating time-based features...")
    transactions_df['year'] = transactions_df['transaction_date'].dt.year
    transactions_df['month'] = transactions_df['transaction_date'].dt.month
    transactions_df['year_month'] = transactions_df['transaction_date'].dt.strftime('%Y-%m')
    transactions_df['quarter'] = transactions_df['transaction_date'].dt.quarter
    
    # Calculate customer tenure
    print("Calculating customer tenure...")
    current_date = datetime.now()
    customers_df['days_since_signup'] = (current_date - customers_df['signup_date']).dt.days
    customers_df['months_since_signup'] = customers_df['days_since_signup'] / 30.44
    
    # Add subscription status
    print("Adding subscription status...")
    subscriptions_df['is_active'] = (
        (subscriptions_df['start_date'] <= current_date) &
        ((subscriptions_df['end_date'].isna()) | (subscriptions_df['end_date'] > current_date))
    )
    
    # Customer segmentation based on ARR
    subscriptions_df['customer_segment'] = pd.cut(
        subscriptions_df['arr_amount'],
        bins=[0, 600, 2400, 6000, float('inf')],
        labels=['SMB', 'Mid-Market', 'Enterprise', 'Strategic']
    )
    
    # Annualize transaction amounts
    print("Calculating annualized amounts...")
    transactions_df['annualized_amount'] = transactions_df.apply(
        lambda row: row['amount'] * 12 if row['transaction_type'] in ['new', 'expansion', 'contraction'] else abs(row['amount']) * 12,
        axis=1
    )
    
    print("✅ Feature engineering completed")
    
    return customers_df, subscriptions_df, transactions_df

def step4_arr_calculations(subscriptions_df, transactions_df):
    """
    Calculate ARR metrics and create summary tables
    """
    print("\n📊 STEP 4: ARR CALCULATIONS")
    print("=" * 50)
    
    # Calculate current ARR
    print("Calculating current ARR...")
    active_subscriptions = subscriptions_df[subscriptions_df['is_active'] == True]
    current_arr = active_subscriptions['arr_amount'].sum()
    active_customers = len(active_subscriptions)
    
    print(f"Current ARR: ${current_arr:,.0f}")
    print(f"Active customers: {active_customers:,}")
    print(f"ARR per customer: ${current_arr/active_customers:,.0f}")
    
    # Create monthly ARR summary
    print("\nCalculating monthly ARR trends...")
    
    # Get all unique months
    all_months = sorted(transactions_df['year_month'].unique())
    
    monthly_arr_data = []
    
    for month in all_months:
        # Filter transactions for this month
        month_transactions = transactions_df[transactions_df['year_month'] == month]
        
        # Calculate ARR components
        new_arr = month_transactions[month_transactions['transaction_type'] == 'new']['annualized_amount'].sum()
        expansion_arr = month_transactions[month_transactions['transaction_type'] == 'expansion']['annualized_amount'].sum()
        contraction_arr = month_transactions[month_transactions['transaction_type'] == 'contraction']['annualized_amount'].sum()
        churned_arr = month_transactions[month_transactions['transaction_type'] == 'churn']['annualized_amount'].sum()
        
        # Calculate ARR as of month end
        month_date = datetime.strptime(month, '%Y-%m')
        month_end = month_date.replace(day=28) + timedelta(days=4)  # End of month
        month_end = month_end - timedelta(days=month_end.day)
        
        active_subs_month = subscriptions_df[
            (subscriptions_df['start_date'] <= month_end) &
            ((subscriptions_df['end_date'].isna()) | (subscriptions_df['end_date'] > month_end))
        ]
        
        month_arr = active_subs_month['arr_amount'].sum()
        month_customers = len(active_subs_month)
        
        monthly_arr_data.append({
            'month': month,
            'month_date': month_end.strftime('%Y-%m-%d'),
            'new_arr': new_arr,
            'expansion_arr': expansion_arr,
            'contraction_arr': contraction_arr,
            'churned_arr': churned_arr,
            'net_new_arr': new_arr + expansion_arr - contraction_arr - churned_arr,
            'current_arr': month_arr,
            'active_customers': month_customers,
            'arr_per_customer': month_arr / month_customers if month_customers > 0 else 0
        })
    
    arr_summary_df = pd.DataFrame(monthly_arr_data)
    
    # Calculate growth rates
    arr_summary_df['previous_arr'] = arr_summary_df['current_arr'].shift(1)
    arr_summary_df['arr_growth_amount'] = arr_summary_df['current_arr'] - arr_summary_df['previous_arr']
    arr_summary_df['arr_growth_rate'] = (arr_summary_df['arr_growth_amount'] / arr_summary_df['previous_arr'] * 100).round(2)
    
    # Create ARR rollforward (bridge) table
    print("Creating ARR rollforward bridge...")
    
    rollforward_data = []
    for i, row in arr_summary_df.iterrows():
        starting_arr = 0 if i == 0 else arr_summary_df.iloc[i-1]['current_arr']
        
        rollforward_data.append({
            'month': row['month'],
            'starting_arr': starting_arr,
            'new_arr': row['new_arr'],
            'expansion_arr': row['expansion_arr'],
            'contraction_arr': -row['contraction_arr'],  # Negative for waterfall
            'churned_arr': -row['churned_arr'],  # Negative for waterfall  
            'ending_arr': row['current_arr'],
            'net_change': row['net_new_arr'],
            'growth_rate': row['arr_growth_rate']
        })
    
    arr_rollforward_df = pd.DataFrame(rollforward_data)
    
    print(f"✅ Created monthly ARR summary for {len(monthly_arr_data)} months")
    print(f"✅ Created ARR rollforward bridge table")
    
    return arr_summary_df, arr_rollforward_df

def step5_export_clean_data(customers_df, subscriptions_df, transactions_df, arr_summary_df, arr_rollforward_df):
    """
    Export all cleaned and calculated data to Excel/CSV files
    """
    print("\n💾 STEP 5: EXPORTING CLEAN DATA")
    print("=" * 50)
    
    # Create output directory
    output_dir = 'cleaned_arr_data'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Export individual CSV files
    customers_df.to_csv(f'{output_dir}/customers_clean.csv', index=False)
    subscriptions_df.to_csv(f'{output_dir}/subscriptions_clean.csv', index=False)
    transactions_df.to_csv(f'{output_dir}/transactions_clean.csv', index=False)
    arr_summary_df.to_csv(f'{output_dir}/arr_monthly_summary.csv', index=False)
    arr_rollforward_df.to_csv(f'{output_dir}/arr_rollforward.csv', index=False)
    
    # Export to single Excel file with multiple sheets
    with pd.ExcelWriter(f'{output_dir}/saas_arr_complete.xlsx', engine='openpyxl') as writer:
        customers_df.to_excel(writer, sheet_name='Customers', index=False)
        subscriptions_df.to_excel(writer, sheet_name='Subscriptions', index=False)
        transactions_df.to_excel(writer, sheet_name='Transactions', index=False)
        arr_summary_df.to_excel(writer, sheet_name='ARR_Monthly_Summary', index=False)
        arr_rollforward_df.to_excel(writer, sheet_name='ARR_Rollforward', index=False)
    
    print(f"✅ Exported all files to '{output_dir}/' directory")
    print(f"✅ Created single Excel file: 'saas_arr_complete.xlsx'")
    
    # Show file locations
    print(f"\n📁 Files created:")
    for file in os.listdir(output_dir):
        print(f"   • {output_dir}/{file}")

def step6_data_validation(arr_summary_df, arr_rollforward_df):
    """
    Validate ARR calculations
    """
    print("\n🔍 STEP 6: DATA VALIDATION")
    print("=" * 50)
    
    # Get latest month data
    latest_month = arr_summary_df.iloc[-1]
    
    print(f"📈 Current ARR Metrics:")
    print(f"   Current ARR: ${latest_month['current_arr']:,.0f}")
    print(f"   Active Customers: {latest_month['active_customers']:,}")
    print(f"   ARR per Customer: ${latest_month['arr_per_customer']:,.0f}")
    print(f"   Latest Growth Rate: {latest_month['arr_growth_rate']:.1f}%")
    
    # Validation checks
    validation_issues = []
    
    # Check ARR per customer range
    avg_arr_per_customer = latest_month['arr_per_customer']
    if avg_arr_per_customer < 300 or avg_arr_per_customer > 5000:
        validation_issues.append(f"ARR per customer (${avg_arr_per_customer:.0f}) outside expected range ($300-$5000)")
    
    # Check growth rate reasonableness
    avg_growth = arr_summary_df['arr_growth_rate'].mean()
    if avg_growth < -10 or avg_growth > 50:
        validation_issues.append(f"Average growth rate ({avg_growth:.1f}%) seems unrealistic")
    
    # Check rollforward math
    rollforward_check = arr_rollforward_df.iloc[-1]
    calculated_ending = (rollforward_check['starting_arr'] + rollforward_check['new_arr'] + 
                        rollforward_check['expansion_arr'] + rollforward_check['contraction_arr'] + 
                        rollforward_check['churned_arr'])
    
    if abs(calculated_ending - rollforward_check['ending_arr']) > 100:
        validation_issues.append("ARR rollforward math doesn't add up correctly")
    
    # Display validation results
    if validation_issues:
        print(f"\n⚠️ Validation Issues Found:")
        for issue in validation_issues:
            print(f"   • {issue}")
    else:
        print(f"\n✅ All validation checks passed!")
        print(f"   • ARR per customer is realistic")
        print(f"   • Growth rates are reasonable") 
        print(f"   • Rollforward math is correct")
    
    return len(validation_issues) == 0

def main():
    """
    Run the complete data engineering pipeline
    """
    print("🚀 SaaS ARR Data Engineering Pipeline")
    print("=" * 60)
    
    # Step 1: Data Ingestion
    customers_df, subscriptions_df, transactions_df = step1_data_ingestion()
    
    if customers_df is None:
        print("❌ Pipeline stopped - please check your CSV files")
        return
    
    # Step 2: Data Cleaning
    customers_clean, subscriptions_clean, transactions_clean = step2_data_cleaning(
        customers_df, subscriptions_df, transactions_df
    )
    
    # Step 3: Feature Engineering
    customers_clean, subscriptions_clean, transactions_clean = step3_feature_engineering(
        customers_clean, subscriptions_clean, transactions_clean
    )
    
    # Step 4: ARR Calculations
    arr_summary_df, arr_rollforward_df = step4_arr_calculations(subscriptions_clean, transactions_clean)
    
    # Step 5: Export Clean Data
    step5_export_clean_data(customers_clean, subscriptions_clean, transactions_clean, 
                           arr_summary_df, arr_rollforward_df)
    
    # Step 6: Validation
    validation_passed = step6_data_validation(arr_summary_df, arr_rollforward_df)
    
    # Final summary
    print(f"\n🎯 PIPELINE COMPLETED")
    print("=" * 60)
    
    if validation_passed:
        print("✅ Data is ready for dashboard creation!")
        print("✅ All files exported to 'cleaned_arr_data/' directory")
        print("✅ You can now upload 'saas_arr_complete.xlsx' to Google Sheets")
    else:
        print("⚠️ Please review validation issues before proceeding")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Upload 'saas_arr_complete.xlsx' to Google Drive")
    print(f"2. Open in Google Sheets")
    print(f"3. Connect to Looker Studio")
    print(f"4. Build ARR dashboard")

if __name__ == "__main__":
    main()
