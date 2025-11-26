import matplotlib.pyplot as plt
import io
import urllib, base64

def get_plot(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close(fig)
    return uri

def generate_order_status_chart(orders):
    status_counts = {}
    for order in orders:
        status = order.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if not status_counts:
        return None

    labels = list(status_counts.keys())
    sizes = list(status_counts.values())
    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99', '#c2c2f0', '#ffb3e6']

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(sizes, labels=labels, colors=colors[:len(labels)], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title("Order Status Distribution")
    
    return get_plot(fig)

def generate_user_role_chart(users):
    staff_count = users.filter(is_staff=True).count()
    regular_count = users.filter(is_staff=False).count()
    
    if staff_count == 0 and regular_count == 0:
        return None

    labels = ['Staff', 'Regular Users']
    sizes = [staff_count, regular_count]
    colors = ['#ff9999','#66b3ff']

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title("User Role Distribution")
    
    return get_plot(fig)

def generate_sales_chart(items):
    # Top 5 items by revenue
    # Assuming items is a list of dicts with 'item' and 'total_revenue' keys as prepared in views.py
    # Or if it's a queryset, we might need to adjust.
    # Let's assume we pass the prepared sales_data list from views.py
    
    sorted_items = sorted(items, key=lambda x: x['total_revenue'], reverse=True)[:5]
    
    if not sorted_items:
        return None

    names = [data['item'].name for data in sorted_items]
    revenues = [data['total_revenue'] for data in sorted_items]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(names, revenues, color='purple')
    
    plt.xlabel('Bakery Item')
    plt.ylabel('Revenue (Kshs)')
    plt.title('Top 5 Items by Revenue')
    plt.xticks(rotation=45, ha='right')
    
    return get_plot(fig)

def generate_subscription_chart(subscriptions):
    # Subscriptions by month (simplified for now, just total vs new this month visual?)
    # Or maybe just a simple bar chart of total subscriptions if we don't have historical data easily accessible in this context.
    # Let's just do a simple pie chart of "New this Month" vs "Older" for now as it's easier with current data passed.
    
    from django.utils import timezone
    now = timezone.now()
    total = subscriptions.count()
    new_this_month = subscriptions.filter(date_subscribed__month=now.month, date_subscribed__year=now.year).count()
    older = total - new_this_month
    
    if total == 0:
        return None
        
    labels = ['New This Month', 'Existing']
    sizes = [new_this_month, older]
    colors = ['#99ff99','#ffcc99']
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title("Subscription Growth")
    
    return get_plot(fig)
