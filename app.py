import streamlit as st
import datetime
from bank import (
    Bank, Account, SavingsAccount, CurrentAccount, 
    Transaction, BankError, AccountNotFoundError, 
    InsufficientBalanceError, AuthenticationError, AccountLockedError
)

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pitom Bank", page_icon="🏦", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #1f77b4;
        color: white;
    }
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'bank' not in st.session_state:
    st.session_state.bank = Bank()
    # Pre-populate with Alice and Bob
    st.session_state.bank.add_account(SavingsAccount("Alice Johnson", "SAV001", 1000.0, "1234", 0.015))
    st.session_state.bank.add_account(CurrentAccount("Bob Smith", "CUR002", 500.0, "5678", 500.0))

if 'user' not in st.session_state:
    st.session_state.user = None

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# --- HELPER FUNCTIONS ---
def login_user(acc_no, pin):
    try:
        account = st.session_state.bank.get_account(acc_no)
        if account.verify_pin(pin):
            st.session_state.user = account
            st.success(f"Welcome back, {account._name}!")
            return True
        else:
            st.error("Invalid PIN.")
    except BankError as e:
        st.error(f"Login failed: {e}")
    return False

def logout():
    st.session_state.user = None
    st.session_state.admin_logged_in = False
    st.rerun()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🏦 Pitom Bank")
if st.session_state.user:
    st.sidebar.info(f"Logged in as: **{st.session_state.user._name}**")
    if st.sidebar.button("Logout"):
        logout()
    menu = ["ATM Dashboard", "Transaction History", "Profile"]
elif st.session_state.admin_logged_in:
    st.sidebar.warning("ADMIN SESSION")
    if st.sidebar.button("Logout"):
        logout()
    menu = ["Admin Dashboard", "System Health"]
else:
    menu = ["Home", "User Login", "Admin Login", "Open New Account"]

selection = st.sidebar.radio("Navigation", menu)

# --- HOME PAGE ---
if selection == "Home":
    st.title("Welcome to Pitom Bank Limited")
    st.image("https://images.unsplash.com/photo-1501167786227-4cba60f6d58f?auto=format&fit=crop&q=80&w=1000", use_column_width=True)
    st.markdown("""
        ### Premium Banking at Your Fingertips
        At Pitom Bank, we prioritize your security and financial growth.
        - **Savings Accounts**: High interest rates to grow your wealth.
        - **Current Accounts**: Flexible overdraft protection for your daily needs.
        - **Security**: Advanced encryption and account locking for your protection.
    """)
    st.info("💡 Use the sidebar to log in or create a new account.")

# --- USER LOGIN ---
elif selection == "User Login":
    st.title("User Login (ATM)")
    with st.form("login_form"):
        acc_no = st.text_input("Account Number (e.g., SAV001)")
        pin = st.text_input("4-Digit PIN", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if login_user(acc_no, pin):
                st.rerun()

# --- ADMIN LOGIN ---
elif selection == "Admin Login":
    st.title("Admin Access")
    with st.form("admin_form"):
        admin_id = st.text_input("Admin ID")
        admin_pass = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Access Dashboard")
        if submitted:
            if admin_id == "admin" and admin_pass == "admin123":
                st.session_state.admin_logged_in = True
                st.success("Admin Login Successful!")
                st.rerun()
            else:
                st.error("Invalid Admin credentials.")

# --- OPEN NEW ACCOUNT ---
elif selection == "Open New Account":
    st.title("Join Pitom Bank")
    with st.form("register_form"):
        name = st.text_input("Full Name")
        initial_deposit = st.number_input("Initial Deposit ($)", min_value=1.0, value=100.0)
        pin = st.text_input("Set 4-Digit Security PIN", type="password", max_chars=4)
        acc_type = st.selectbox("Account Type", ["Savings (1.5% Interest)", "Current ($500 Overdraft)"])
        submitted = st.form_submit_button("Create Account")
        
        if submitted:
            if not name or len(pin) != 4:
                st.error("Please provide a name and a 4-digit PIN.")
            else:
                acc_no = f"ACC{len(st.session_state.bank.accounts) + 1:03d}"
                if "Savings" in acc_type:
                    new_acc = SavingsAccount(name, acc_no, initial_deposit, pin, 0.015)
                else:
                    new_acc = CurrentAccount(name, acc_no, initial_deposit, pin, 500.0)
                
                st.session_state.bank.add_account(new_acc)
                st.balloons()
                st.success(f"Welcome to the family! Your Account Number is: **{acc_no}**")

# --- USER DASHBOARD ---
elif selection == "ATM Dashboard":
    st.title(f"ATM Dashboard")
    user = st.session_state.user
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Account Operations")
        tab1, tab2, tab3 = st.tabs(["Deposit", "Withdraw", "Transfer"])
        
        with tab1:
            amount_d = st.number_input("Deposit Amount", min_value=1.0, key="dep_amt")
            if st.button("Confirm Deposit"):
                try:
                    user.deposit(amount_d)
                    st.success(f"Deposited ${amount_d} successfully.")
                    st.rerun()
                except BankError as e:
                    st.error(e)
        
        with tab2:
            amount_w = st.number_input("Withdraw Amount", min_value=1.0, key="with_amt")
            if st.button("Confirm Withdrawal"):
                try:
                    user.withdraw(amount_w)
                    st.success(f"Withdrew ${amount_w} successfully.")
                    st.rerun()
                except BankError as e:
                    st.error(e)
        
        with tab3:
            target_no = st.text_input("Target Account Number", key="trans_target")
            amount_t = st.number_input("Transfer Amount", min_value=1.0, key="trans_amt")
            if st.button("Confirm Transfer"):
                try:
                    target_acc = st.session_state.bank.get_account(target_no)
                    user.transfer(target_acc, amount_t)
                    st.success(f"Transferred ${amount_t} to {target_no}.")
                    st.rerun()
                except BankError as e:
                    st.error(e)

    with col2:
        st.metric("Available Balance", f"${user.check_balance():.2f}")
        st.info(f"**Account No:** {user._acc_no}\n\n**Type:** {type(user).__name__}")

# --- TRANSACTION HISTORY ---
elif selection == "Transaction History":
    st.title("Transaction Logs")
    user = st.session_state.user
    history = user.get_transaction_history()
    
    if not history:
        st.write("No transactions recorded yet.")
    else:
        # Convert objects to data for table
        data = []
        for tx in history:
            data.append({
                "Timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "ID": tx.transaction_id[:8],
                "Type": tx.type,
                "Amount": f"${tx.amount:.2f}",
                "Balance After": f"${tx.balance_after:.2f}"
            })
        st.dataframe(data, use_container_width=True)

# --- PROFILE ---
elif selection == "Profile":
    st.title("Account Profile")
    user = st.session_state.user
    st.json({
        "Name": user._name,
        "Account Number": user._acc_no,
        "Account Type": type(user).__name__,
        "Current Balance": user._balance,
        "Status": "Locked" if user._is_locked else "Active"
    })

# --- ADMIN DASHBOARD ---
elif selection == "Admin Dashboard":
    st.title("Bank Administration")
    bank = st.session_state.bank
    
    st.subheader("Manage Accounts")
    acc_data = []
    for acc_no, acc in bank.accounts.items():
        acc_data.append({
            "Acc No": acc_no,
            "Owner": acc._name,
            "Balance": f"${acc._balance:.2f}",
            "Status": "🔴 Locked" if acc._is_locked else "🟢 Active"
        })
    st.dataframe(acc_data, use_container_width=True)
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        target_block = st.text_input("Enter Acc No to Block/Unlock")
        if st.button("Toggle Lock Status"):
            try:
                account = bank.get_account(target_block)
                if account._is_locked:
                    account.unlock_account()
                    st.success(f"Account {target_block} unlocked.")
                else:
                    account.lock_account()
                    st.warning(f"Account {target_block} locked.")
                st.rerun()
            except BankError as e:
                st.error(e)
    with col2:
        if st.button("Apply Interest (All Savings)"):
            count = 0
            for acc in bank.accounts.values():
                if isinstance(acc, SavingsAccount):
                    acc.add_interest()
                    count += 1
            st.success(f"Interest applied to {count} Savings Accounts.")
            st.rerun()
