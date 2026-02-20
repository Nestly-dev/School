# 📚 Book Hub — Book Discovery App

A full-stack book discovery application built with React + TypeScript (frontend) and Node.js + Express + MongoDB (backend).

---

## 🔧 Prerequisites

Before you start, install the following on your computer:

- **Node.js v18+** → [https://nodejs.org](https://nodejs.org)
- **npm v9+** (comes with Node.js)
- **Git** → [https://git-scm.com](https://git-scm.com)

Verify everything is installed:

```bash
node --version   # Should show v18.x.x or higher
npm --version    # Should show 9.x.x or higher
git --version    # Should show git version x.x.x
```

---

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

> Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with the actual GitHub username and repo name.

---

## 2️⃣ Set Up MongoDB Atlas (Free Cloud Database)

The app uses MongoDB Atlas as its database. Follow these steps to create a free one:

**a) Create an account**
- Go to [https://cloud.mongodb.com](https://cloud.mongodb.com) and sign up for free

**b) Create a cluster**
- Click **+ Create** and choose the **M0 Free** tier
- Pick any region and click **Create Deployment**

**c) Create a database user**
- When prompted, set a username and password
- Use a simple password with **no special characters** like `@`, `#`, or `/` (e.g. `bookhub123`)
- Click **Create Database User**

**d) Allow your IP address**
- Go to **Security → Network Access**
- Click **+ Add IP Address**
- Click **Allow Access From Anywhere** (adds `0.0.0.0/0`)
- Click **Confirm**

**e) Get your connection string**
- Go to **Database → Clusters**
- Click **Connect** → **Drivers**
- Copy the connection string. It looks like:
  ```
  mongodb+srv://youruser:yourpassword@cluster0.xxxxx.mongodb.net/
  ```
- Add `/bookhub` at the end:
  ```
  mongodb+srv://youruser:yourpassword@cluster0.xxxxx.mongodb.net/bookhub
  ```

---

## 3️⃣ Set Up the Backend

```bash
# Navigate to the backend folder
cd bookhub-backend

# Install dependencies
npm install
```

**Create a `.env` file** inside `bookhub-backend/`:

```bash
touch .env
```

Open it and paste the following, filling in your own values:

```env
PORT=5000
MONGO_URI=mongodb+srv://youruser:yourpassword@cluster0.xxxxx.mongodb.net/bookhub
JWT_SECRET=anyrandomsecretstringhere
JWT_EXPIRES_IN=7d
FRONTEND_URL=http://localhost:5173
```

> ⚠️ Replace `MONGO_URI` with your actual Atlas connection string from Step 2e.

---

## 4️⃣ Seed the Database

This command fills your database with sample books and creates two demo accounts:

```bash
node src/seed.js
```

You should see:

```
✅ Connected to MongoDB
🗑️  Cleared existing data
✅ Created 8 books
📋 Demo credentials:
   Admin → admin@bookhub.com / admin123
   User  → user@bookhub.com  / user1234
🎉 Seed complete!
```

---

## 5️⃣ Start the Backend Server

```bash
npm run dev
```

You should see:

```
✅ Connected to MongoDB
🚀 Server running on http://localhost:5000
```

> Keep this terminal open. The backend must stay running.

---

## 6️⃣ Set Up and Start the Frontend

Open a **new terminal window** (keep the backend running in the first one):

```bash
# Navigate to the frontend folder
cd bookhub-frontend

# Install dependencies
npm install

# Start the frontend
npm run dev
```

You should see:

```
VITE v7.x.x  ready in 167 ms
➜  Local:   http://localhost:5173/
```

---

## 7️⃣ Open the App

Go to **[http://localhost:5173](http://localhost:5173)** in your browser.

The app should load with books on the homepage. ✅

---

## 🔑 Demo Login Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@bookhub.com | admin123 |
| **Regular User** | user@bookhub.com | user1234 |

Log in as **admin** to access the Admin Dashboard, manage books, and view analytics.

---

## 📂 Folder Structure

```
/
├── bookhub-backend/      ← Express API + MongoDB
│   ├── src/
│   │   ├── models/       ← User and Book schemas
│   │   ├── routes/       ← auth, books, admin endpoints
│   │   ├── middleware/   ← JWT authentication
│   │   ├── server.js     ← App entry point
│   │   └── seed.js       ← Database seeder
│   └── .env              ← Your environment variables (not committed to git)
│
└── bookhub-frontend/     ← React + TypeScript + Vite
    └── src/
        ├── components/   ← Navbar, BookCard, FilterPanel, Pagination
        ├── context/      ← Auth Context (login/logout state)
        ├── store/        ← Redux (filter/search state)
        ├── pages/        ← Home, BookDetail, Login, Register, Admin pages
        ├── types/        ← TypeScript interfaces
        └── utils/        ← Axios API client
```

---

## 🚀 Quick Start (After First-Time Setup)

Once you've completed the setup above, you only need two commands to run the app:

**Terminal 1 — Backend:**
```bash
cd bookhub-backend
npm run dev
```

**Terminal 2 — Frontend:**
```bash
cd bookhub-frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## ⚠️ Troubleshooting

### White screen on the frontend
Open browser DevTools (`F12` or `Cmd+Option+I` on Mac) → **Console** tab and look for red errors. Make sure all files exist in `src/store/` (`index.ts`, `hooks.ts`, `filterSlice.ts`).

### MongoDB connection error
```
Could not connect to any servers in your MongoDB Atlas cluster
```
- Make sure your IP is whitelisted in Atlas → **Security → Network Access**
- Double-check your `MONGO_URI` in `.env` — correct password, no typos, ends with `/bookhub`

### Authentication failed
```
bad auth: authentication failed
```
- Go to Atlas → **Security → Database Access** → Edit your user → reset the password
- Update the password in your `.env` — avoid special characters (`@`, `#`, `/`)

### Port already in use
Change `PORT=5000` to `PORT=5001` in `.env` and restart the backend.

### `next is not a function` error when seeding
Open `bookhub-backend/src/models/User.js` and update the pre-save hook:

```js
// Replace this:
userSchema.pre('save', async function (next) {
  if (!this.isModified('password')) return next();
  this.password = await bcrypt.hash(this.password, 12);
  next();
});

// With this:
userSchema.pre('save', async function () {
  if (!this.isModified('password')) return;
  this.password = await bcrypt.hash(this.password, 12);
});
```

---

## 📄 License

This project is for educational purposes as part of the ALU BSE programme.