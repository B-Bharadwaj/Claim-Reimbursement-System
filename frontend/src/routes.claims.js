import Icon from "@mui/material/Icon";

// Pages
import SubmitClaim from "layouts/employee/submit-claim";
import MyClaims from "layouts/employee/my-claims";
import ReviewClaims from "layouts/manager/review-claims";
import Payments from "layouts/finance/payments";

export default function getRoleRoutes(role) {
  // role expected: "EMPLOYEE" | "MANAGER" | "FINANCE"
  if (role === "MANAGER") {
    return [
      {
        type: "collapse",
        name: "Review Claims",
        key: "review-claims",
        icon: <Icon fontSize="small">fact_check</Icon>,
        route: "/manager/review-claims",
        component: <ReviewClaims />,
      },
    ];
  }

  if (role === "FINANCE") {
    return [
      {
        type: "collapse",
        name: "Payments",
        key: "payments",
        icon: <Icon fontSize="small">payments</Icon>,
        route: "/finance/payments",
        component: <Payments />,
      },
    ];
  }

  // default EMPLOYEE
  return [
    {
      type: "collapse",
      name: "Submit Claim",
      key: "submit-claim",
      icon: <Icon fontSize="small">add_circle</Icon>,
      route: "/employee/submit-claim",
      component: <SubmitClaim />,
    },
    {
      type: "collapse",
      name: "My Claims",
      key: "my-claims",
      icon: <Icon fontSize="small">receipt_long</Icon>,
      route: "/employee/my-claims",
      component: <MyClaims />,
    },
  ];
}
