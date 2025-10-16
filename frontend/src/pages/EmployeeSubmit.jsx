import { useState } from "react";
import api from "../api/axios";

export default function EmployeeSubmit() {
  const [form, setForm] = useState({ title: "", amount: "", description: "" });
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append("title", form.title);
      formData.append("amount", form.amount);
      formData.append("description", form.description);
      if (file) formData.append("receipt", file);

      await api.post("expenses/", formData);
      setMessage("✅ Expense submitted successfully!");
      setForm({ title: "", amount: "", description: "" });
      setFile(null);
    } catch (err) {
      console.error(err);
      setMessage("❌ Error submitting expense. Check console.");
    }
  };

  return (
    <div className="max-w-lg mx-auto bg-white text-black shadow p-6 rounded-lg">
      <h2 className="text-2xl font-semibold mb-4">Submit Expense</h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <input
          name="title"
          placeholder="Expense title"
          value={form.title}
          onChange={handleChange}
          className="border p-2 rounded"
          required
        />
        <input
          name="amount"
          type="number"
          placeholder="Amount"
          value={form.amount}
          onChange={handleChange}
          className="border p-2 rounded"
          required
        />
        <textarea
          name="description"
          placeholder="Description"
          value={form.description}
          onChange={handleChange}
          className="border p-2 rounded"
        />
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          className="border p-2 rounded"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
        >
          Submit
        </button>
      </form>
      {message && <p className="mt-4 text-center">{message}</p>}
    </div>
  );
}
