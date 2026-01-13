import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "context/AuthContext";

export default function ProtectedRoute({ children, allowedRoles }) {
  const { token, role } = useContext(AuthContext);

  if (!token) return <Navigate to="/authentication/sign-in" replace />;

  if (!allowedRoles.includes(role)) return <Navigate to="/unauthorized" replace />;

  return children;
}
import PropTypes from "prop-types";

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
  allowedRoles: PropTypes.array.isRequired,
};
