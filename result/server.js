
const express = require("express");
const { Pool } = require("pg");
const path = require("path");

const app = express();
const port = 3000;

const pool = new Pool({
  host: process.env.DB_HOST || "db",
  user: process.env.POSTGRES_USER || "postgres",
  password: process.env.POSTGRES_PASSWORD || "postgres",
  database: process.env.POSTGRES_DB || "postgres",
  port: 5432,
});

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "views", "index.html"));
});

app.get("/api/results", async (req, res) => {
  try {
    const result = await pool.query(
      "SELECT vote, COUNT(id) AS count FROM votes GROUP BY vote"
    );
    const votes = { a: 0, b: 0 };
    result.rows.forEach((row) => {
      votes[row.vote] = parseInt(row.count);
    });
    res.json(votes);
  } catch (err) {
    res.json({ a: 0, b: 0 });
  }
});

app.listen(port, "0.0.0.0", () => {
  console.log(`Result app listening on port ${port}`);
});
