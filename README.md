# 🎬 Movie Ticket Booking System

A fully functional **Python-based movie ticket booking system** with a graphical interface, **MySQL** database integration, **UPI QR code generation**, and real-time **seat selection**. Designed for smooth user experience and ease of booking, cancellation, and payment.

---

## 🚀 Features

- 🔐 **User Authentication** (Sign Up / Sign In / Delete Account)
- 🎟️ **Seat Booking** with 10x10 live grid (color-coded)
- 💺 **Seat Types**: Non AC | AC | First Class
- 🗓️ **Date-based movie scheduling**
- 📲 **UPI QR Code Generator** for seamless payments
- 📄 **Receipt Generation** for booking/cancellation
- 🔎 **Ticket Checking & Account Info**
- 🧾 **MySQL** powered backend.

---

## 📸 GUI Screenshots

### 🔐 Sign In / Sign Up  
![Sign In](screenshots/signin.png)

---




### 💽 MySQL User Table  
![Database](screenshots/db-user_accounts.png)

---

### 🎫 Ticket Booking  
![Ticket Booking](screenshots/ticketbooking.png)

---

### 🧾 UPI QR Code  
![QR Code](screenshots/qrcode.png)

---

### ✅ Seat Booking + Receipt  
![Seat Receipt](screenshots/setabooked.png)

---

### 🔍 Ticket Checking  
![Ticket Checking](screenshots/ticket_checking.png)

---

### ❌ Ticket Cancellation  
![Ticket Cancellation](screenshots/ticket_cancelling.png)

---


---

## 🛠️ Tech Stack

| Tool       | Purpose                            |
|------------|------------------------------------|
| `Python`   | Core language                      |
| `Tkinter`  | GUI for seat grid and input        |
| `MySQL`    | Database for user and ticket data  |
| `qrcode`   | QR code generation for UPI payment |
| `datetime` | Date handling and booking logic    |

---

## ⚙️ Setup Instructions
### 1. Install Dependencies

pip install mysql-connector-python

pip install qrcode[pil]

### 2. Clone the Repo

```bash
git clone https://github.com/YourUsername/Movie-ticket-bookking.git
cd Movie-ticket-bookking
