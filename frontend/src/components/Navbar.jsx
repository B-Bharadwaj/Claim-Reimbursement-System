import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="bg-gray-900 text-white p-4 flex gap-6">
      <Link to="/" className="font-semibold hover:text-gray-300">Submit Expense</Link>
      <Link to="/my-expenses" className="font-semibold hover:text-gray-300">My Expenses</Link>
      <Link to="/manager" className="font-semibold hover:text-gray-300">Pending Approvals</Link>
      <Link to="/finance" className="font-semibold hover:text-gray-300">Ready for Payment</Link>
    </nav>
  );
}
