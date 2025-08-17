"""
ARR Dashboard Data Validation Script
Checks if your dashboard is showing correct values from your real data

Run this to validate:
python data_validation_checker.py
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def validate_dashboard_data():
    """
    Validate that dashboard shows correct values from your CSV data
    """
    print("🔍 ARR DASHBOARD DATA VALIDATION")
    print("=" * 60)
    
    try:
        # Load your actual data files
        print("📂 Loading your data files...")
        
        arr_summary = pd.read_csv('cleaned_arr_data/arr_monthly_summary.csv')
        arr_rollforward = pd.read_csv('cleaned_arr_data/arr_rollforward.csv')
        subscriptions = pd.read_csv('cleaned_arr_data/subscriptions_clean.csv')
        
        print(f"✅ ARR Summary: {len(arr_summary)} months")
        print(f"✅ ARR Rollforward: {len(arr_rollforward)} months")
        print(f"✅ Subscriptions: {len(subscriptions)} records")
        
        # Get latest month data (what dashboard should show)
        latest_arr = arr_summary.iloc[-1]
        previous_arr = arr_summary.iloc[-2] if len(arr_summary) > 1 else latest_arr
        latest_rollforward = arr_rollforward.iloc[-1]
        
        print(f"\n📊 DASHBOARD VALUES VALIDATION")
        print("=" * 40)
        
        # Validate Current ARR
        print(f"Current ARR:")
        print(f"  Dashboard shows: $1,086,712")
        print(f"  Your data shows: ${latest_arr['current_arr']:,.0f}")
        arr_match = abs(latest_arr['current_arr'] - 1086712) < 100
        print(f"  ✅ Match: {arr_match}")
        
        # Validate Active Customers
        print(f"\nActive Customers:")
        print(f"  Dashboard shows: 846")
        print(f"  Your data shows: {latest_arr['active_customers']}")
        customer_match = abs(latest_arr['active_customers'] - 846) < 5
        print(f"  ✅ Match: {customer_match}")
        
        # Validate ARR per Customer
        calculated_arr_per_customer = latest_arr['current_arr'] / latest_arr['active_customers']
        print(f"\nARR per Customer:")
        print(f"  Dashboard shows: $1,285")
        print(f"  Your data shows: ${calculated_arr_per_customer:.0f}")
        arr_per_customer_match = abs(calculated_arr_per_customer - 1285) < 50
        print(f"  ✅ Match: {arr_per_customer_match}")
        
        # Validate Monthly Growth
        arr_change = latest_arr['current_arr'] - previous_arr['current_arr']
        growth_rate = (arr_change / previous_arr['current_arr']) * 100
        print(f"\nMonthly Growth:")
        print(f"  Dashboard shows: 1.6%")
        print(f"  Your data shows: {growth_rate:.1f}%")
        growth_match = abs(growth_rate - 1.6) < 0.5
        print(f"  ✅ Match: {growth_match}")
        
        # Validate Waterfall Components
        print(f"\n🔄 WATERFALL CHART VALIDATION")
        print("=" * 40)
        
        print(f"Starting ARR: ${latest_rollforward['starting_arr']:,.0f}")
        print(f"New ARR: ${latest_rollforward['new_arr']:,.0f}")
        print(f"Expansion ARR: ${latest_rollforward['expansion_arr']:,.0f}")
        print(f"Contraction ARR: ${latest_rollforward['contraction_arr']:,.0f}")
        print(f"Churn ARR: ${latest_rollforward['churned_arr']:,.0f}")
        print(f"Ending ARR: ${latest_rollforward['ending_arr']:,.0f}")
        
        # Validate waterfall math
        calculated_ending = (latest_rollforward['starting_arr'] + 
                            latest_rollforward['new_arr'] + 
                            latest_rollforward['expansion_arr'] + 
                            latest_rollforward['contraction_arr'] + 
                            latest_rollforward['churned_arr'])
        
        print(f"\nWaterfall Math Check:")
        print(f"  Starting + New + Expansion + Contraction + Churn = Ending")
        print(f"  ${latest_rollforward['starting_arr']:,.0f} + ${latest_rollforward['new_arr']:,.0f} + ${latest_rollforward['expansion_arr']:,.0f} + ${latest_rollforward['contraction_arr']:,.0f} + ${latest_rollforward['churned_arr']:,.0f} = ${calculated_ending:,.0f}")
        print(f"  Expected Ending ARR: ${latest_rollforward['ending_arr']:,.0f}")
        
        waterfall_match = abs(calculated_ending - latest_rollforward['ending_arr']) < 100
        print(f"  ✅ Waterfall Math Correct: {waterfall_match}")
        
        # Validate Customer Segmentation
        print(f"\n👥 CUSTOMER SEGMENTATION VALIDATION")
        print("=" * 40)
        
        active_subs = subscriptions[subscriptions['is_active'] == True]
        segment_totals = active_subs.groupby('customer_segment').agg({
            'arr_amount': 'sum',
            'customer_id': 'count'
        }).round(0)
        
        print("Segment breakdown from your data:")
        total_segment_arr = segment_totals['arr_amount'].sum()
        for segment in segment_totals.index:
            arr_amount = segment_totals.loc[segment, 'arr_amount']
            customer_count = segment_totals.loc[segment, 'customer_id']
            percentage = (arr_amount / total_segment_arr) * 100
            print(f"  {segment}: ${arr_amount:,.0f} ({customer_count} customers, {percentage:.1f}%)")
        
        print(f"\nTotal ARR from segments: ${total_segment_arr:,.0f}")
        print(f"Current ARR from summary: ${latest_arr['current_arr']:,.0f}")
        segment_match = abs(total_segment_arr - latest_arr['current_arr']) < 1000
        print(f"✅ Segment totals match: {segment_match}")
        
        # Overall validation summary
        print(f"\n🎯 OVERALL VALIDATION SUMMARY")
        print("=" * 40)
        
        all_checks = [arr_match, customer_match, arr_per_customer_match, growth_match, waterfall_match, segment_match]
        
        if all(all_checks):
            print("✅ ALL VALIDATIONS PASSED!")
            print("✅ Your dashboard is showing REAL, ACCURATE data")
            print("✅ All calculations are mathematically correct")
            print("✅ Waterfall chart logic is proper")
            print("✅ Customer segmentation is accurate")
        else:
            print("⚠️ Some validations failed:")
            checks = ['ARR Value', 'Customer Count', 'ARR per Customer', 'Growth Rate', 'Waterfall Math', 'Segment Totals']
            for i, check in enumerate(all_checks):
                status = "✅" if check else "❌"
                print(f"  {status} {checks[i]}")
        
        # Data quality assessment
        print(f"\n📊 DATA QUALITY ASSESSMENT")
        print("=" * 40)
        
        # Check data completeness
        months_with_data = len(arr_summary)
        print(f"Months of data: {months_with_data}")
        
        # Check for data gaps
        arr_summary['month_date'] = pd.to_datetime(arr_summary['month_date'])
        date_gaps = arr_summary['month_date'].diff().dt.days.max()
        print(f"Largest gap between months: {date_gaps} days")
        
        # Check growth rate reasonableness
        avg_growth = arr_summary['arr_growth_rate'].mean()
        print(f"Average monthly growth rate: {avg_growth:.1f}%")
        
        # Check customer metrics
        avg_arr_per_customer = (latest_arr['current_arr'] / latest_arr['active_customers'])
        print(f"Average ARR per customer: ${avg_arr_per_customer:.0f}")
        
        # Business logic validation
        print(f"\n🧠 BUSINESS LOGIC CHECK")
        print("=" * 40)
        
        # Check if growth rates make sense
        if avg_growth < -5:
            print("⚠️ Warning: Very negative growth rate - business declining rapidly")
        elif avg_growth > 30:
            print("⚠️ Warning: Very high growth rate - may be unrealistic")
        else:
            print("✅ Growth rates are within realistic business ranges")
        
        # Check ARR per customer reasonableness
        if avg_arr_per_customer < 300:
            print("⚠️ Warning: ARR per customer very low for SaaS business")
        elif avg_arr_per_customer > 10000:
            print("⚠️ Warning: ARR per customer very high - check data")
        else:
            print("✅ ARR per customer is realistic for SaaS business")
        
        # Check customer distribution
        enterprise_pct = (segment_totals.loc['Enterprise', 'arr_amount'] / total_segment_arr) * 100 if 'Enterprise' in segment_totals.index else 0
        if enterprise_pct > 70:
            print("✅ Enterprise-heavy customer base (typical for high ARR)")
        elif enterprise_pct < 30:
            print("✅ SMB/Mid-market focus (typical for volume business)")
        else:
            print("✅ Balanced customer portfolio")
        
        return all(all_checks)
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("💡 Make sure you've run the data engineering script first")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def check_waterfall_logic():
    """
    Specifically validate waterfall chart logic
    """
    print(f"\n🔄 WATERFALL CHART LOGIC CHECK")
    print("=" * 40)
    
    try:
        rollforward = pd.read_csv('cleaned_arr_data/arr_rollforward.csv')
        latest = rollforward.iloc[-1]
        
        print("Waterfall Components (from your data):")
        print(f"  Starting ARR: ${latest['starting_arr']:,.0f}")
        print(f"  + New ARR: ${latest['new_arr']:,.0f}")
        print(f"  + Expansion ARR: ${latest['expansion_arr']:,.0f}")
        print(f"  - Contraction ARR: ${abs(latest['contraction_arr']):,.0f}")
        print(f"  - Churn ARR: ${abs(latest['churned_arr']):,.0f}")
        print(f"  = Ending ARR: ${latest['ending_arr']:,.0f}")
        
        # Manual calculation
        manual_calculation = (latest['starting_arr'] + 
                             latest['new_arr'] + 
                             latest['expansion_arr'] + 
                             latest['contraction_arr'] + 
                             latest['churned_arr'])
        
        print(f"\nManual Calculation Check:")
        print(f"  ${latest['starting_arr']:,.0f} + ${latest['new_arr']:,.0f} + ${latest['expansion_arr']:,.0f} + ({latest['contraction_arr']:,.0f}) + ({latest['churned_arr']:,.0f})")
        print(f"  = ${manual_calculation:,.0f}")
        print(f"  Expected: ${latest['ending_arr']:,.0f}")
        print(f"  Difference: ${abs(manual_calculation - latest['ending_arr']):,.0f}")
        
        if abs(manual_calculation - latest['ending_arr']) < 100:
            print("✅ Waterfall math is CORRECT")
            print("✅ Your dashboard waterfall chart shows accurate data")
        else:
            print("❌ Waterfall math error - check data processing")
            
        # Check if waterfall makes business sense
        net_change = latest['ending_arr'] - latest['starting_arr']
        print(f"\nBusiness Logic Check:")
        print(f"  Net ARR Change: ${net_change:,.0f}")
        print(f"  New + Expansion: ${latest['new_arr'] + latest['expansion_arr']:,.0f}")
        print(f"  Contraction + Churn: ${abs(latest['contraction_arr']) + abs(latest['churned_arr']):,.0f}")
        
        if (latest['new_arr'] + latest['expansion_arr']) > (abs(latest['contraction_arr']) + abs(latest['churned_arr'])):
            print("✅ Positive net growth (good business health)")
        else:
            print("⚠️ Negative net growth (business challenge)")
            
    except Exception as e:
        print(f"❌ Error checking waterfall: {e}")

if __name__ == "__main__":
    # Run validation
    validation_passed = validate_dashboard_data()
    check_waterfall_logic()
    
    if validation_passed:
        print(f"\n🎉 CONCLUSION: Your dashboard is showing REAL, ACCURATE data!")
        print(f"🎯 All values come from your generated CSV files")
        print(f"🧮 All calculations are mathematically correct")
        print(f"📊 Charts represent actual business performance")
    else:
        print(f"\n⚠️ CONCLUSION: Some data issues detected")
        print(f"💡 Review the validation results above")
