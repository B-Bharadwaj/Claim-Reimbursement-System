/* eslint-disable prettier/prettier */
import PropTypes from "prop-types";

// @mui material components
import Grid from "@mui/material/Grid";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";

// Layout container
import PageLayout from "examples/LayoutContainers/PageLayout";

function BasicLayout({ children }) {
  return (
    <PageLayout>
      {/* Plain background */}
      <MDBox
        width="100%"
        minHeight="100vh"
        display="flex"
        justifyContent="center"
        alignItems="center"
        bgcolor="#f5f6fa"   // light neutral background
      >
        <Grid container justifyContent="center" alignItems="center">
          <Grid item xs={11} sm={9} md={5} lg={4} xl={3}>
            {children}
          </Grid>
        </Grid>
      </MDBox>
    </PageLayout>
  );
}

// Typechecking props for the BasicLayout
BasicLayout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default BasicLayout;
