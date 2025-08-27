import mysql.connector as sql
import tkinter as tk
from tkinter import messagebox, simpledialog
import datetime
import qrcode

class DatabaseConnection:
    def __init__(self):
        self.connection = sql.connect(
            host='localhost',
            user='root',
            passwd='tiger',
            port=3306,
            database='pvrmovie'
        )
        self.cursor = self.connection.cursor(buffered=True)

    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
        except sql.Error as err:
            print(f"Error: {err}")
            self.connection.rollback()

    def fetch_one(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except sql.Error as err:
            print(f"Error: {err}")
            return None

    def fetch_all(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sql.Error as err:
            print(f"Error: {err}")
            return None

    def __del__(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()

class MovieTicketBookingSystem:
    def __init__(self):
        self.db = DatabaseConnection()
        self.window = tk.Tk()
        self.window.title("Movie Ticket Booking System")
        self.window.geometry("500x600")

        self.seats = []
        self.selected_seats = []
        self.create_seat_grid()
        self.create_input_field()

        self.phone = ""
        self.gender = ""
        self.num_tickets = 0

    def create_seat_grid(self):
        seat_frame = tk.Frame(self.window)
        seat_frame.pack(pady=20)

        for i in range(10):
            row = []
            for j in range(10):
                seat = tk.Button(seat_frame, text=f"{i+1}{j+1}", command=lambda row=i, column=j: self.select_seat(row, column), height=2, width=4)
                seat.grid(row=i, column=j, padx=2, pady=2)
                row.append(seat)
            self.seats.append(row)

        self.book_button = tk.Button(self.window, text="Book Seats", command=self.book_seats)
        self.book_button.pack(pady=10)

    def create_input_field(self):
        self.input_field = tk.Entry(self.window, width=30)
        self.input_field.pack(pady=10)
        self.input_field.bind("<Return>", self.handle_input)

        instruction_label = tk.Label(self.window, text="Type 'clear' to reset seats or 'cancel' to cancel a booking")
        instruction_label.pack()

    def select_seat(self, row, column):
        seat = self.seats[row][column]
        seat_id = f"{row+1}{column+1}"

        if seat['bg'] == 'red':
            messagebox.showerror("Error", "This seat is already booked.")
        elif seat['bg'] == 'green':
            seat['bg'] = 'SystemButtonFace'
            self.selected_seats.remove(seat_id)
        else:
            seat['bg'] = 'green'
            self.selected_seats.append(seat_id)

    def generate_receipt(self, action, seats, movie, seat_type, cost):
        receipt = f"""
        ===== PVR LOGIX IMAX THEATRE =====
        Receipt for Ticket {action.capitalize()}

        Movie: {movie}
        Date: {datetime.date.today().strftime("%Y-%m-%d")}
        Seat Type: {seat_type}
        Seats: {', '.join(seats)}
        Total Cost: {cost} Rs

        Thank you for choosing PVR LOGIX IMAX THEATRE!
        =======================================
        """
        return receipt

    def book_seats(self):
        if self.selected_seats:
            movie = self.current_movie
            seat_type = self.current_seat_type
            cost_per_seat = self.current_cost_per_seat
            booking_date = datetime.date.today().strftime("%Y-%m-%d")

            if seat_type == '1':
                table = 'non_ac'
                seat_type_name = "Non AC"
            elif seat_type == '2':
                table = 'ac'
                seat_type_name = "AC"
            elif seat_type == '3':
                table = 'firstclass'
                seat_type_name = "First Class"
            else:
                messagebox.showerror("Error", "Invalid seat type")
                return

            try:
                check_query = f"SELECT booked_seats FROM {table} WHERE mname = %s AND Date = %s"
                result = self.db.fetch_one(check_query, (movie, booking_date))

                if result:
                    existing_seats = result[0] if result[0] else ""
                    new_seats = existing_seats + "," + ",".join(self.selected_seats) if existing_seats else ",".join(self.selected_seats)
                    update_query = f"UPDATE {table} SET booked_seats = %s, Gender = %s, tkts = %s, phno = %s WHERE mname = %s AND Date = %s"
                    self.db.execute_query(update_query, (new_seats, self.gender, self.num_tickets, self.phone, movie, booking_date))
                else:
                    insert_query = f"INSERT INTO {table} (mname, Date, booked_seats, Gender, tkts, phno) VALUES (%s, %s, %s, %s, %s, %s)"
                    self.db.execute_query(insert_query, (movie, booking_date, ",".join(self.selected_seats), self.gender, self.num_tickets, self.phone))

                cost = len(self.selected_seats) * cost_per_seat
                receipt = self.generate_receipt("booking", self.selected_seats, movie, seat_type_name, cost)
                messagebox.showinfo("Booking Successful", f"You have booked the following seats: {', '.join(self.selected_seats)}\nTotal cost: {cost} Rs\n\nReceipt:\n{receipt}")
                self.generate_upi_qr_code(cost)
                
                for seat in self.selected_seats:
                    row, col = int(seat[0])-1, int(seat[1])-1
                    self.seats[row][col]['bg'] = 'red'
                
                self.selected_seats = []

            except Exception as e:
                messagebox.showerror("Error", f"Failed to update booked seats: {str(e)}")
        else:
            messagebox.showerror("Error", "Please select at least one seat to book.")

    def generate_upi_qr_code(self, cost):
        upi_id = "6397749277@paytm"
        upi_url = f"upi://{upi_id}?amount={cost}&currency=INR&purpose=Payment"
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(upi_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"upi_qr_code_{upi_id}_{cost}.png")
        print(f"UPI QR code generated and saved as upi_qr_code_{upi_id}_{cost}.png")

    def handle_input(self, event):
        user_input = self.input_field.get().strip().lower()
        if user_input == "clear":
            if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all booked seats?"):
                self.reset_seat_colors()
                self.input_field.delete(0, tk.END)
        elif user_input == "cancel":
            self.cancel_ticket()
        self.input_field.delete(0, tk.END)

    def reset_seat_colors(self):
        for row in self.seats:
            for seat in row:
                if seat['bg'] == 'red':
                    seat['bg'] = 'SystemButtonFace'

    def cancel_ticket(self):
        movie = simpledialog.askstring("Cancel Ticket", "Enter the movie name:")
        seat_type = simpledialog.askstring("Cancel Ticket", "Enter seat type (1 for NON AC, 2 for AC, 3 for FIRST CLASS):")
        if not movie or not seat_type:
            return

        if seat_type == '1':
            table = 'non_ac'
            seat_type_name = "Non AC"
        elif seat_type == '2':
            table = 'ac'
            seat_type_name = "AC"
        elif seat_type == '3':
            table = 'firstclass'
            seat_type_name = "First Class"
        else:
            messagebox.showerror("Error", "Invalid seat type")
            return

        try:
            query = f"SELECT booked_seats FROM {table} WHERE mname = %s AND Date = %s"
            result = self.db.fetch_one(query, (movie, datetime.date.today().strftime("%Y-%m-%d")))
            if result and result[0]:
                booked_seats = result[0].split(',')
                seat_to_cancel = simpledialog.askstring("Cancel Ticket", f"Booked seats: {', '.join(booked_seats)}\nEnter the seat number to cancel:")
                if seat_to_cancel in booked_seats:
                    booked_seats.remove(seat_to_cancel)
                    update_query = f"UPDATE {table} SET booked_seats = %s WHERE mname = %s AND Date = %s"
                    self.db.execute_query(update_query, (','.join(booked_seats), movie, datetime.date.today().strftime("%Y-%m-%d")))
                    
                    row, col = int(seat_to_cancel[0])-1, int(seat_to_cancel[1])-1
                    self.seats[row][col]['bg'] = 'SystemButtonFace'
                    
                    cost = self.current_cost_per_seat
                    receipt = self.generate_receipt("cancellation", [seat_to_cancel], movie, seat_type_name, cost)
                    messagebox.showinfo("Cancellation Successful", f"Ticket for seat {seat_to_cancel} has been cancelled.\n\nReceipt:\n{receipt}")
                else:
                    messagebox.showerror("Error", "Invalid seat number")
            else:
                messagebox.showerror("Error", "No booked seats found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel ticket: {str(e)}")

    def run(self, movie, seat_type, cost_per_seat, phone, gender, num_tickets):
        self.current_movie = movie
        self.current_seat_type = seat_type
        self.current_cost_per_seat = cost_per_seat
        self.phone = phone
        self.gender = gender
        self.num_tickets = num_tickets
        self.load_booked_seats()
        self.window.mainloop()

    def load_booked_seats(self):
        try:
            if self.current_seat_type == '1':
                table = 'non_ac'
            elif self.current_seat_type == '2':
                table = 'ac'
            elif self.current_seat_type == '3':
                table = 'firstclass'
            else:
                raise ValueError("Invalid seat type")

            query = f"SELECT booked_seats FROM {table} WHERE mname = %s AND Date = %s"
            result = self.db.fetch_one(query, (self.current_movie, datetime.date.today().strftime("%Y-%m-%d")))
            if result and result[0]:
                booked_seats = result[0].split(',')
                for seat in booked_seats:
                    if seat:
                        row, col = int(seat[0])-1, int(seat[1])-1
                        self.seats[row][col]['bg'] = 'red'
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load booked seats: {str(e)}")

class MovieBookingSystem:
    def __init__(self):
        self.db = DatabaseConnection()

    def menu(self):
        while True:
            print('\nWELCOME TO PVR LOGIX IMAX THEATRE BOOKING, NEW DELHI (AC & NON AC)')
            print('1. SIGN IN')
            print('2. SIGN UP')
            print('3. DELETE ACCOUNT')
            print('4. EXIT')
            choice = input('ENTER YOUR CHOICE (1,2,3,4): ')
            
            if choice == '1':
                if self.sign_in():
                    self.main_menu()
            elif choice == '2':
                if self.sign_up():
                    self.main_menu()
            elif choice == '3':
                if self.delete_account():
                    print('ACCOUNT DELETED')
                else:
                    print('YOUR PASSWORD OR USER NAME IS INCORRECT')
            elif choice == '4':
                print('THANK YOU')
                break
            else:
                print('PLEASE ENTER A VALID INPUT, TRY AGAIN')

    def sign_in(self):
        username = input('USER NAME: ')
        password = input('PASSWORD: ')
        user = self.db.fetch_one("SELECT * FROM user_accounts WHERE user_name = %s AND password = %s", (username, password))
        if user:
            print(f'WELCOME {user[0]} {user[1]}')
            return True
        else:
            print('ACCOUNT DOES NOT EXIST')
            return False

    def sign_up(self):
        first_name = input("FIRST NAME: ")
        last_name = input("LAST NAME: ")
        username = input('USER NAME: ')
        password = input('PASSWORD: ')
        confirm_password = input('RE-ENTER YOUR PASSWORD: ')
        phone = input("PHONE NUMBER (91+): ")
        if not phone.startswith(("6", "7", "8", "9")) or len(phone) != 10:
            print("Enter a Valid phone number")
            return False
        gender = input('ENTER YOUR GENDER (m/f/n): ')
        dob = input("DATE OF BIRTH (DD-MM-YYYY): ")
        age = input('YOUR AGE: ')

        if password != confirm_password:
            print('PASSWORDS DO NOT MATCH, PLEASE RETRY')
            return False

        existing_user = self.db.fetch_one("SELECT * FROM user_accounts WHERE user_name = %s", (username,))
        if existing_user:
            print('SORRY, USERNAME ALREADY EXISTS, PLEASE CHOOSE A DIFFERENT USERNAME')
            return False

        existing_phoneno = self.db.fetch_one("SELECT * FROM user_accounts WHERE PHNO = %s", (phone,))
        if existing_phoneno:
            print('SORRY, THIS PHONE NUMBER IS ALREADY IN USE, PLEASE CHOOSE A DIFFERENT PHONE NUMBER')
            return False

        try:
            dob_date = datetime.datetime.strptime(dob, '%d-%m-%Y').date()
            formatted_dob = dob_date.strftime('%Y-%m-%d')

            self.db.execute_query(
                "INSERT INTO user_accounts (fname, lname, user_name, password, phno, gender, dob, age) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (first_name, last_name, username, password, phone, gender, formatted_dob, age)
            )
            print(f'WELCOME {first_name} {last_name}')
            return True
        except ValueError:
            print("Invalid date format. Please use DD-MM-YYYY.")
            return False
        except Exception as e:
            print(f'AN ERROR OCCURRED: {str(e)}')
            return False

    def delete_account(self):
        username = input('USER NAME: ')
        password = input('PASSWORD: ')
        user = self.db.fetch_one("SELECT * FROM user_accounts WHERE user_name = %s AND password = %s", (username, password))
        if user:
            print('IS THIS YOUR ACCOUNT?')
            print(f"Name: {user[0]} {user[1]}")
            print(f"Phone: {user[4]}")
            print(f"Gender: {user[5]}")
            print(f"Date of Birth: {user[6]}")
            print(f"Age: {user[7]}")
            confirm = input('Enter 1 to confirm deletion, any other key to cancel: ')
            if confirm == '1':
                self.db.execute_query("DELETE FROM user_accounts WHERE user_name = %s AND password = %s", (username, password))
                return True
        return False

    def main_menu(self):
        while True:
            print('\n1. TICKET BOOKING')
            print('2. TICKET CHECKING')
            print('3. TICKET CANCELLING')
            print('4. ACCOUNT DETAILS')
            print('5. LOG OUT')
            choice = input('Enter your choice (1,2,3,4,5): ')
            
            if choice == '1':
                self.ticket_booking()
            elif choice == '2':
                self.ticket_checking()
            elif choice == '3':
                self.ticket_cancelling()
            elif choice == '4':
                self.account_details()
            elif choice == '5':
                print('THANK YOU')
                break
            else:
                print('WRONG INPUT')

    def ticket_booking(self):
        print("\n****PVR LOGIX IMAX THEATRE BOOKING (AC & NON AC)****")
        print("1. NON AC  Price=200Rs")
        print("2. AC  Price=400Rs")
        print("3. FIRST CLASS  Price=700Rs")
        seat_type = input("Enter your choice (1,2,3): ")
        
        date = self.get_valid_date()
        if not date:
            return

        movies = self.get_movies_for_date(date)
        if not movies:
            print("Movies not available for this date, please try again later")
            return

        for i, movie in enumerate(movies, 1):
            print(f"{i}. {movie}")
        
        movie_choice = int(input("Enter the movie number: "))
        if movie_choice < 1 or movie_choice > len(movies):
            print("Invalid movie choice")
            return

        movie_name = movies[movie_choice-1]
        cost_per_seat = self.get_price(seat_type)

        phone = input("Enter your phone number (91+): ")
        if not phone.startswith(("6", "7", "8", "9")) or len(phone) != 10:
            print("Enter a valid phone number")
            return

        gender = input("Enter your gender (m/f/n): ")
        if gender not in ['m', 'f', 'n']:
            print("Invalid gender")
            return

        num_tickets = int(input("Enter number of tickets: "))
        if num_tickets <= 0 or num_tickets > 10:
            print("Invalid number of tickets")
            return

        booking_system = MovieTicketBookingSystem()
        booking_system.run(movie_name, seat_type, cost_per_seat, phone, gender, num_tickets)

    def ticket_checking(self):
        phone = input('Enter your phone number(91+): ')
        if not phone.startswith(("6", "7", "8", "9")) or len(phone) != 10:
            print("Enter a Valid phone number")
            return False
        
        try:
            tickets = []
            for table in ['non_ac', 'ac', 'firstclass']:
                query = f"SELECT * FROM {table} WHERE phno = %s"
                result = self.db.fetch_all(query, (phone,))
                tickets.extend(result)
            
            if tickets:
                for ticket in tickets:
                    print("\nTicket Details:")
                    print(f"Movie: {ticket[0]}")
                    print(f"Gender: {ticket[1]}")
                    print(f"Date: {ticket[2]}")
                    print(f"Number of tickets: {ticket[3]}")
                    print(f"Phone: {ticket[4]}")
                    print(f"Booked seats: {ticket[5]}")
                    print(f"Seat Type: {'Non AC' if table == 'non_ac' else 'AC' if table == 'ac' else 'First Class'}")
            else:
                print('No tickets found for this phone number.')
        except Exception as e:
            print("An error occurred while checking the ticket. Please try again or contact us.")
            print(f"Error details: {str(e)}")

    def ticket_cancelling(self):
        phone = input('Enter your phone number(91+): ')
        if not phone.startswith(("6", "7", "8", "9")) or len(phone) != 10:
            print("Enter a Valid phone number")
            return False
        
        try:
            tickets = []
            for table in ['non_ac', 'ac', 'firstclass']:
                query = f"SELECT * FROM {table} WHERE phno = %s"
                result = self.db.fetch_all(query, (phone,))
                tickets.extend([(table, ticket) for ticket in result])
            
            if tickets:
                print("\nYour Tickets:")
                for i, (table, ticket) in enumerate(tickets, 1):
                    print(f"{i}. Movie: {ticket[0]}, Date: {ticket[2]}, Seats: {ticket[5]}, Type: {table}")
                
                choice = int(input("Enter the number of the ticket you want to cancel (0 to abort): "))
                if 0 < choice <= len(tickets):
                    table, ticket = tickets[choice - 1]
                    confirm = input(f"Are you sure you want to cancel this ticket? (y/n): ")
                    if confirm.lower() == 'y':
                        delete_query = f"DELETE FROM {table} WHERE phno = %s AND mname = %s AND Date = %s"
                        self.db.execute_query(delete_query, (phone, ticket[0], ticket[2]))
                        print('TICKET CANCELLED. YOUR MONEY HAS BEEN REFUNDED SUCCESSFULLY.')
                    else:
                        print("Cancellation aborted.")
                elif choice == 0:
                    print("Cancellation aborted.")
                else:
                    print("Invalid choice.")
            else:
                print("No tickets found for this phone number.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def account_details(self):
        username = input('USER NAME: ')
        password = input('PASSWORD: ')
        user = self.db.fetch_one("SELECT * FROM user_accounts WHERE user_name = %s AND password = %s", (username, password))
        if user:
            print(f"First Name: {user[0]}")
            print(f"Last Name: {user[1]}")
            print(f"Phone Number: {user[4]}")
            print(f"Gender: {user[5]}")
            print(f"Date of Birth: {user[6]}")
            print(f"Age: {user[7]}")
        else:
            print('ACCOUNT DOES NOT EXIST')

    def get_valid_date(self):
        while True:
            try:
                day = int(input("Enter day (DD): "))
                month = int(input("Enter month (MM): "))
                year = int(input("Enter year (YYYY): "))
                date = datetime.date(year, month, day)
                today = datetime.date.today()
                if date < today:
                    print("Date cannot be in the past")
                elif (date - today).days > 4:
                    print("Can only book up to 4 days in advance")
                else:
                    return date
            except ValueError:
                print("Invalid date, please try again")

    def get_movies_for_date(self, date):
        # Fixed list of 5 movies that will be displayed every day
        movies = [
            "VENOM ZEHER KA KAEHER (Hindi dub) Timings:10am to 1pm",
            "JEENE NHI DUNGA (Hindi dub) Timings:2pm to 4pm",
            "PUSHPA 2 (Hindi dub) Timings:7pm to 9pm",
            "RED NOTICE 2 (English) Timings:10am to 12pm",
            "KANCHNA 2 (Horror) Timings:1pm to 3pm"
        ]
        return movies

    def get_price(self, seat_type):
        prices = {'1': 200, '2': 400, '3': 700}
        return prices.get(seat_type, 200)

import os

if __name__ == "__main__":
    if os.name == 'nt':  # Windows
        os.system('mode con lines=200 cols=200')  # Set terminal window size
        os.system('COLOR 70')  # Set terminal color (light green on black)
    else:
        pass  # For non-Windows, no action is taken

    booking_system = MovieBookingSystem()
    booking_system.menu()
