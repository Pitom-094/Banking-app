# Bank Management System using Python OOP
import datetime
import uuid
from abc import ABC, abstractmethod

class BankError(Exception):
    """Base class for all bank-related errors."""
    pass

class InsufficientBalanceError(BankError):
    pass

class InvalidAmountError(BankError):
    pass

class AuthenticationError(BankError):
    pass

class AccountNotFoundError(BankError):
    pass

class AccountLockedError(BankError):
    pass

class DuplicateAccountError(BankError):
    pass

class Bank:
    bank_name = "Pitom Bank Limited"

    def __init__(self):
        self.accounts = {}

    def add_account(self, account):
        if account._acc_no in self.accounts:
            raise DuplicateAccountError(f"Account {account._acc_no} already exists.")
        self.accounts[account._acc_no] = account
        print(f"Account {account._acc_no} added successfully to {self.bank_name}")

    def del_account(self, account_number):
        if account_number in self.accounts:
            del self.accounts[account_number]
            print(f"Account {account_number} deleted successfully.")
        else:
            raise AccountNotFoundError(f"Account {account_number} not found.")

    def get_account(self, account_number):
        if account_number in self.accounts:
            return self.accounts[account_number]
        else:
            raise AccountNotFoundError(f"Account {account_number} not found.")

    def account_exists(self, account_number):
        return account_number in self.accounts

# account
class Account:
    def __init__(self, name, acc_no, balance, pin):
        self._name = name
        self._acc_no = acc_no
        self._balance = balance
        self._pin = pin
        self._transactions = []
        self._is_locked = False
        self._failed_attempts = 0

    def deposit(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Amount must be positive.")
        self._balance += amount
        self.add_transaction(Transaction("Deposit", amount, self._balance))
        print("Deposit successful")

    def withdraw(self, amount):
        if self._is_locked:
            raise AccountLockedError("Account is locked due to multiple failed attempts.")
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive.")
        if self._balance < amount:
            raise InsufficientBalanceError(f"Insufficient funds. Available: {self._balance}")
        
        self._balance -= amount
        self.add_transaction(Transaction("Withdraw", amount, self._balance))
        print("Withdraw successful")

    def transfer(self, target_account, amount):
        if self._is_locked:
            raise AccountLockedError("Source account is locked.")
        if amount <= 0:
            raise InvalidAmountError("Transfer amount must be positive.")
        if self._balance < amount:
            raise InsufficientBalanceError(f"Insufficient funds for transfer. Available: {self._balance}")
        
        self._balance -= amount
        target_account.deposit(amount)
        self.add_transaction(Transaction("Transfer", amount, self._balance))
        print("Transfer successful")

    def check_balance(self):
        return self._balance

    def get_transaction_history(self):
        return self._transactions

    def verify_pin(self, pin):
        if self._is_locked:
            raise AccountLockedError("Access denied. Account is locked.")
        if self._pin == pin:
            self.reset_failed_attempts()
            return True
        else:
            self.increment_failed_attempts()
            return False

    def lock_account(self):
        self._is_locked = True
        print("Account has been locked.")

    def unlock_account(self):
        self._is_locked = False
        self.reset_failed_attempts()
        print("Account has been unlocked.")

    def increment_failed_attempts(self):
        self._failed_attempts += 1
        if self._failed_attempts >= 3:
            self.lock_account()

    def reset_failed_attempts(self):
        self._failed_attempts = 0

    def add_transaction(self, transaction):
        self._transactions.append(transaction)

    def display_info(self):
        print("--- Account Info ---")
        print(f"Name: {self._name}")
        print(f"Account: {self._acc_no}")
        print(f"Balance: {self._balance}")
        print(f"Is Locked: {self._is_locked}")

class SavingsAccount(Account):
    def __init__(self, name, acc_no, balance, pin, interest_rate):
        super().__init__(name, acc_no, balance, pin)
        self.interest_rate = interest_rate

    def calculate_interest(self):
        return self._balance * self.interest_rate

    def add_interest(self):
        interest = self.calculate_interest()
        if interest > 0:
            self._balance += interest
            self.add_transaction(Transaction("Deposit", interest, self._balance))
            print(f"Interest of {interest} added successfully.")

class CurrentAccount(Account):
    def __init__(self, name, acc_no, balance, pin, overdraft_limit):
        super().__init__(name, acc_no, balance, pin)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount):
        if self._is_locked:
            raise AccountLockedError("Account is locked.")
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive.")
        if (self._balance + self.overdraft_limit) < amount:
            raise InsufficientBalanceError(f"Insufficient funds including overdraft. Available: {self._balance + self.overdraft_limit}")
        
        self._balance -= amount
        self.add_transaction(Transaction("Withdraw", amount, self._balance))
        print("Withdraw successful")

class Transaction:
    def __init__(self, type, amount, balance_after):
        self.transaction_id = str(uuid.uuid4())
        self.type = type
        self.amount = amount
        self.timestamp = datetime.datetime.now()
        self.balance_after = balance_after

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.transaction_id} - {self.type}: {self.amount} (Balance: {self.balance_after})"

    def get_summary(self):
        return f"{self.type} of {self.amount} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}. New balance: {self.balance_after}"

class ATM(ABC):
    @abstractmethod
    def authenticate(self, acc_no, pin):
        pass

    @abstractmethod
    def withdraw_cash(self, amount):
        pass

    @abstractmethod
    def deposit_cash(self, amount):
        pass

    @abstractmethod
    def check_balance(self):
        pass

    @abstractmethod
    def transfer_money(self, target_acc_no, amount):
        pass

    @abstractmethod
    def show_menu(self):
        pass

class ATMmachine(ATM):
    def __init__(self, bank_instance, max_attempts=3):
        self.bank = bank_instance
        self.current_account = None
        self.session_active = False
        self.max_attempts = max_attempts

    def authenticate(self, acc_no, pin):
        try:
            if acc_no in self.bank.accounts:
                account = self.bank.accounts[acc_no]
                if account.verify_pin(pin):
                    self.current_account = account
                    self.session_active = True
                    print(f"Welcome back, {account._name}!")
                    return True
                else:
                    print("Invalid PIN.")
            else:
                raise AccountNotFoundError(f"Account {acc_no} not found.")
            return False
        except BankError as e:
            print(f"Authentication failed: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def logout(self):
        self.current_account = None
        self.session_active = False
        print("Session ended. Thank you for using Pitom Bank.")

    def withdraw_cash(self, amount):
        if not self.session_active:
            print("Error: Authentication required.")
            return
        try:
            self.current_account.withdraw(amount)
        except BankError as e:
            print(f"Withdrawal failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def deposit_cash(self, amount):
        if not self.session_active:
            print("Error: Authentication required.")
            return
        try:
            self.current_account.deposit(amount)
        except BankError as e:
            print(f"Deposit failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def check_balance(self):
        if not self.session_active:
            print("Error: Authentication required.")
            return
        try:
            balance = self.current_account.check_balance()
            print(f"Available Balance: {balance}")
        except BankError as e:
            print(f"Balance check failed: {e}")
        except Exception as e:
            print(f"Error retrieving balance: {e}")

    def transfer_money(self, target_acc_no, amount):
        if not self.session_active:
            print("Error: Authentication required.")
            return
        try:
            if target_acc_no in self.bank.accounts:
                target_account = self.bank.accounts[target_acc_no]
                self.current_account.transfer(target_account, amount)
            else:
                raise AccountNotFoundError(f"Target account {target_acc_no} not found.")
        except BankError as e:
            print(f"Transfer failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def view_account_details(self):
        if not self.session_active:
            print("Error: Authentication required.")
            return
        self.current_account.display_info()

    def view_transaction_history(self):
        if not self.session_active:
            print("Error: Authentication required.")
            return
        print("\n--- Transaction History ---")
        history = self.current_account.get_transaction_history()
        if not history:
            print("No transactions found.")
        else:
            for tx in history:
                print(tx.get_summary())

    def show_menu(self):
        while self.session_active:
            self.display_menu()

    def display_menu(self):
        print("\n" + "="*20)
        print("  PITOM BANK ATM")
        print("="*20)
        print("1. Check Balance")
        print("2. Deposit Cash")
        print("3. Withdraw Cash")
        print("4. Transfer Money")
        print("5. View Profile")
        print("6. Transaction History")
        print("7. Logout")
        print("="*20)
        choice = input("Please select an option (1-7): ")
        self.handle_user_choice(choice)

    def handle_user_choice(self, choice):
        try:
            if choice == '1':
                self.check_balance()
            elif choice == '2':
                amount = float(input("Enter deposit amount: "))
                self.deposit_cash(amount)
            elif choice == '3':
                amount = float(input("Enter withdrawal amount: "))
                self.withdraw_cash(amount)
            elif choice == '4':
                target = input("Enter target account number: ")
                amount = float(input("Enter transfer amount: "))
                self.transfer_money(target, amount)
            elif choice == '5':
                self.view_account_details()
            elif choice == '6':
                self.view_transaction_history()
            elif choice == '7':
                self.logout()
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Error: Please enter a valid numerical amount.")
        except Exception as e:
            
            print(f"Error processing request: {e}")

class Admin:
    def __init__(self, admin_id, password, bank_instance):
        self.admin_id = admin_id
        self.password = password
        self.bank = bank_instance

    def view_all_accounts(self):
        print("\n" + "="*30)
        print("  ADMIN: ALL ACCOUNTS")
        print("="*30)
        if not self.bank.accounts:
            print("No accounts found in the system.")
        else:
            for acc_no, account in self.bank.accounts.items():
                status = "LOCKED" if account._is_locked else "ACTIVE"
                print(f"Acc: {acc_no} | Owner: {account._name} | Balance: {account._balance} | Status: {status}")
        print("="*30)

    def block_account(self, acc_no):
        try:
            if acc_no in self.bank.accounts:
                self.bank.accounts[acc_no].lock_account()
            else:
                raise AccountNotFoundError(f"Account {acc_no} not found.")
        except BankError as e:
            print(f"Admin action failed: {e}")

    def unlock_account(self, acc_no):
        try:
            if acc_no in self.bank.accounts:
                self.bank.accounts[acc_no].unlock_account()
            else:
                raise AccountNotFoundError(f"Account {acc_no} not found.")
        except BankError as e:
            print(f"Admin action failed: {e}")

if __name__ == "__main__":
    # Initialize the system
    pitom_bank = Bank()
    
    # Pre-populate some accounts for immediate use
    pitom_bank.add_account(SavingsAccount("Alice Johnson", "SAV001", 1000.0, "1234", 0.015))
    pitom_bank.add_account(CurrentAccount("Bob Smith", "CUR002", 500.0, "5678", 500.0))
    
    atm = ATMmachine(pitom_bank)
    # Default Admin credentials: admin / admin123
    admin = Admin("admin", "admin123", pitom_bank)

    while True:
        print("\n" + "╔" + "═"*33 + "╗")
        print("║      PITOM BANKING SYSTEM       ║")
        print("╠" + "═"*33 + "╣")
        print("║  1. User Login (ATM)            ║")
        print("║  2. Admin Login                 ║")
        print("║  3. Open New Account            ║")
        print("║  4. System Info / Help          ║")
        print("║  5. Exit                        ║")
        print("╚" + "═"*33 + "╝")
        
        main_choice = input("Please select an option: ")

        if main_choice == '1':
            print("\n--- ATM LOGIN ---")
            acc_no = input("Enter Account Number: ")
            pin = input("Enter PIN: ")
            if atm.authenticate(acc_no, pin):
                atm.show_menu()
        
        elif main_choice == '2':
            print("\n--- ADMIN LOGIN ---")
            user_id = input("Enter Admin ID: ")
            password = input("Enter Admin Password: ")
            
            if user_id == admin.admin_id and password == admin.password:
                print("\n[✔] Admin Access Granted.")
                while True:
                    print("\n--- ADMIN DASHBOARD ---")
                    print("1. View All Accounts")
                    print("2. Block an Account")
                    print("3. Unlock an Account")
                    print("4. Admin Logout")
                    
                    admin_choice = input("Select an option: ")
                    
                    if admin_choice == '1':
                        admin.view_all_accounts()
                    elif admin_choice == '2':
                        acc = input("Enter Account Number to block: ")
                        admin.block_account(acc)
                    elif admin_choice == '3':
                        acc = input("Enter Account Number to unlock: ")
                        admin.unlock_account(acc)
                    elif admin_choice == '4':
                        print("Admin logged out.")
                        break
                    else:
                        print("Invalid selection.")
            else:
                print("[✘] Error: Invalid Admin credentials.")
        
        elif main_choice == '3':
            print("\n--- OPEN NEW ACCOUNT ---")
            name = input("Enter your full name: ")
            try:
                balance = float(input("Enter initial deposit amount: "))
                pin = input("Set your security PIN: ")
                print("Select Account Type:")
                print("1. Savings (1.5% interest rate)")
                print("2. Current ($500 overdraft limit)")
                acc_type_choice = input("Choice (1-2): ")
                
                # Generate a simple unique account number
                acc_no = f"ACC{len(pitom_bank.accounts) + 1:03d}"
                
                if acc_type_choice == '1':
                    new_acc = SavingsAccount(name, acc_no, balance, pin, 0.015)
                elif acc_type_choice == '2':
                    new_acc = CurrentAccount(name, acc_no, balance, pin, 500.0)
                else:
                    print("[!] Error: Invalid account type selection.")
                    continue
                
                pitom_bank.add_account(new_acc)
                print(f"\n[✔] Success! Account created for {name}.")
                print(f"Your Account Number is: {acc_no}")
            except ValueError:
                print("[!] Error: Please enter a valid numeric amount for the deposit.")
            except BankError as e:
                print(f"[!] Registration failed: {e}")

        elif main_choice == '4':
            print("\n" + "="*35)
            print("      SYSTEM INFO / HELP")
            print("="*35)
            print("TEST USER ACCOUNTS:")
            print("- Alice: SAV001 | PIN: 1234")
            print("- Bob  : CUR002 | PIN: 5678")
            print("\nADMIN CREDENTIALS:")
            print("- ID: admin | Pass: admin123")
            print("="*35)

        elif main_choice == '5':
            print("\nThank you for using Pitom Bank. Goodbye!")
            break
        
        else:
            
            print("[!] Invalid choice. Please try again.")

