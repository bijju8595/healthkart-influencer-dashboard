import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Number of records
NUM_INFLUENCERS = 50
NUM_POSTS = 200

# --- 1. Influencers Dataset ---
influencers_data = []
for i in range(1, NUM_INFLUENCERS + 1):
    category = random.choice(['Fitness', 'Wellness', 'Bodybuilding', 'Yoga', 'Nutrition'])
    platform = random.choice(['Instagram', 'YouTube'])
    influencers_data.append({
        'influencer_id': i,
        'name': fake.name(),
        'category': category,
        'gender': random.choice(['Male', 'Female']),
        'follower_count': random.randint(10000, 1000000),
        'platform': platform
    })
influencers = pd.DataFrame(influencers_data)

# --- 2. Posts Dataset ---
posts_data = []
for _ in range(NUM_POSTS):
    influencer = influencers.sample(1).iloc[0]
    posts_data.append({
        'post_id': fake.uuid4(),
        'influencer_id': influencer['influencer_id'],
        'platform': influencer['platform'],
        'date': fake.date_time_between(start_date='-6M', end_date='now'),
        'url': fake.uri(),
        'caption': fake.sentence(nb_words=15),
        'reach': random.randint(5000, 200000),
        'likes': random.randint(500, 20000),
        'comments': random.randint(50, 2000)
    })
posts = pd.DataFrame(posts_data)

# --- 3. Payouts & Tracking Data (Combined Simulation) ---
payouts_data = []
tracking_data = []
start_date = datetime.now() - timedelta(days=180)

for _, influencer in influencers.iterrows():
    basis = random.choice(['per_post', 'per_order'])
    rate = random.uniform(5000, 25000) if basis == 'per_post' else random.uniform(50, 250)
    
    influencer_posts = posts[posts['influencer_id'] == influencer['influencer_id']]
    num_posts = len(influencer_posts)
    
    total_orders = 0
    total_revenue = 0

    if num_posts > 0:
        # Simulate tracking data for each post
        for _, post in influencer_posts.iterrows():
            # More engaging posts lead to more orders
            orders_from_post = int((post['likes'] / 1000) * random.uniform(0.5, 2.0))
            
            for _ in range(orders_from_post):
                revenue_per_order = random.uniform(500, 4000)
                tracking_data.append({
                    'source': influencer['platform'],
                    'campaign': random.choice(['MuscleBlaze_Whey', 'HKVitals_Vitamins', 'Gritzo_Kids']),
                    'influencer_id': influencer['influencer_id'],
                    'user_id': fake.uuid4(),
                    'product': random.choice(['Whey Protein', 'Multivitamin', 'Super Gummy', 'Creatine']),
                    'date': post['date'] + timedelta(days=random.randint(0, 3)),
                    'orders': 1,
                    'revenue': round(revenue_per_order, 2)
                })
                total_orders += 1
                total_revenue += revenue_per_order

    # Calculate total payout based on basis
    if basis == 'per_post':
        total_payout = num_posts * rate
    else: # per_order
        total_payout = total_orders * rate

    payouts_data.append({
        'influencer_id': influencer['influencer_id'],
        'basis': basis,
        'rate': round(rate, 2),
        'orders': total_orders,
        'total_payout': round(total_payout, 2)
    })

payouts = pd.DataFrame(payouts_data)
tracking = pd.DataFrame(tracking_data)


# --- Save to CSV ---
influencers.to_csv('influencers.csv', index=False)
posts.to_csv('posts.csv', index=False)
tracking.to_csv('tracking_data.csv', index=False)
payouts.to_csv('payouts.csv', index=False)

print("✅ Simulated data generated and saved to CSV files.")
print(f"-> influencers.csv: {len(influencers)} rows")
print(f"-> posts.csv: {len(posts)} rows")
print(f"-> tracking_data.csv: {len(tracking)} rows")
print(f"-> payouts.csv: {len(payouts)} rows")