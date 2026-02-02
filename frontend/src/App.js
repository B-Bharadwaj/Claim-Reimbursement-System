/* eslint-disable prettier/prettier */
import SignIn from "layouts/authentication/sign-in";
import { useState, useEffect, useMemo } from "react";

// react-router components
import { Routes, Route, Navigate, useLocation } from "react-router-dom";

// @mui material components
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

// Material Dashboard 2 React example components
import Sidenav from "examples/Sidenav";

// Material Dashboard 2 React themes
import theme from "assets/theme";
import themeRTL from "assets/theme/theme-rtl";

// Material Dashboard 2 React Dark Mode themes
import themeDark from "assets/theme-dark";
import themeDarkRTL from "assets/theme-dark/theme-rtl";

// RTL plugins
import rtlPlugin from "stylis-plugin-rtl";
import { CacheProvider } from "@emotion/react";
import createCache from "@emotion/cache";

// Material Dashboard 2 React routes
import getRoleRoutes from "routes.claims";

// Material Dashboard 2 React contexts
import { useMaterialUIController, setMiniSidenav } from "context";

// Images
import brandWhite from "assets/images/logo-ct.png";
import brandDark from "assets/images/logo-ct-dark.png";

export default function App() {
  const [controller, dispatch] = useMaterialUIController();
  const {
    miniSidenav,
    direction,
    sidenavColor,
    transparentSidenav,
    whiteSidenav,
    darkMode,
  } = controller;

  const [onMouseEnter, setOnMouseEnter] = useState(false);
  const [rtlCache, setRtlCache] = useState(null);

  const { pathname } = useLocation();
  const isAuthRoute = pathname.startsWith("/authentication");
  const role = localStorage.getItem("role") || "EMPLOYEE";
  const routes = useMemo(() => getRoleRoutes(role), [role]);
  const token = localStorage.getItem("access");

  // Cache for RTL
  useEffect(() => {
    const cacheRtl = createCache({
      key: "rtl",
      stylisPlugins: [rtlPlugin],
    });
    setRtlCache(cacheRtl);
  }, []);

  // Open sidenav when mouse enters mini sidenav
  const handleOnMouseEnter = () => {
    if (miniSidenav && !onMouseEnter) {
      setMiniSidenav(dispatch, false);
      setOnMouseEnter(true);
    }
  };

  // Close sidenav when mouse leaves mini sidenav
  const handleOnMouseLeave = () => {
    if (onMouseEnter) {
      setMiniSidenav(dispatch, true);
      setOnMouseEnter(false);
    }
  };

  // Set dir attribute
  useEffect(() => {
    document.body.setAttribute("dir", direction);
  }, [direction]);

  // Scroll to top on route change
  useEffect(() => {
    document.documentElement.scrollTop = 0;
    document.scrollingElement.scrollTop = 0;
  }, [pathname]);

  const getRoutes = (allRoutes) =>
    allRoutes.map((route) => {
      if (route.collapse) return getRoutes(route.collapse);
      if (route.route) return <Route path={route.route} element={route.component} key={route.key} />;
      return null;
    });

  const AppRoutes = (
    <Routes>
      {/* Always allow auth pages */}
      <Route path="/authentication/sign-in" element={<SignIn />} />

      {/* Everything else requires token */}
      {token ? (
        <>
          {getRoutes(routes)}
          <Route
            path="*"
            element={
              <Navigate
                to={
                  role === "MANAGER"
                    ? "/manager/review-claims"
                    : role === "FINANCE"
                    ? "/finance/payments"
                    : "/employee/my-claims"
                }
                replace
              />
            }
          />
        </>
      ) : (
        <>
          <Route path="/" element={<Navigate to="/authentication/sign-in" replace />} />
          <Route path="*" element={<Navigate to="/authentication/sign-in" replace />} />
        </>
      )}
    </Routes>
  );

  const Shell = (
    <>
      <CssBaseline />
      {token && (
        <Sidenav
          color={sidenavColor}
          brand={(transparentSidenav && !darkMode) || whiteSidenav ? brandDark : brandWhite}
          brandName="Claim Reimbursement"
          routes={routes}
          onMouseEnter={handleOnMouseEnter}
          onMouseLeave={handleOnMouseLeave}
        />
      )}
      {AppRoutes}
    </>
  );

  return direction === "rtl" ? (
    <CacheProvider value={rtlCache}>
      <ThemeProvider theme={darkMode ? themeDarkRTL : themeRTL}>{Shell}</ThemeProvider>
    </CacheProvider>
  ) : (
    <ThemeProvider theme={darkMode ? themeDark : theme}>{Shell}</ThemeProvider>
  );
}
