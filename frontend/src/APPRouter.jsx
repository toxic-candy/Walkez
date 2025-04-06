import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import User_Layout from "./Pages/User_Pages/User_Layout";
import User_Home from "./Pages/User_Pages/User_Home";
import User_Login from "./Pages/User_Pages/User_Login";
import User_Register from "./Pages/User_Pages/User_Register";
import User_upload from "./Pages/User_Pages/User_upload";
import User_profile from "./Pages/User_Pages/User_profile";
import User_layout2 from "./Pages/User_Pages/User_layout2";
import User_about from "./Pages/User_Pages/User_about";
import User_services from "./Pages/User_Pages/User_services";
import Admin_layout from "./Pages/admin/admin_layout";
import AdminHomePage from "./Pages/admin/adminHomePage";
import Admin_Login from "./Pages/admin/admin_Login";
import User_contact from "./Pages/User_Pages/User_contact";
import Admin_Register from "./Pages/admin/adminRegister";

import AdminNoti from "./Pages/admin/AdminNoti";
import AdminUser from "./Pages/admin/AdminUser";
import AdminImages from "./Pages/admin/AdminImages";
import Tenent_Register from "./Pages/Tenent/TenentRegister";
import TenentLayout from "./Pages/Tenent/TenentLayout";
import Tenent_Login from "./Pages/Tenent/TenentLogin";
import TenentLoginUserLayout from "./Pages/Tenent/TenentLoginUserLayout";
import TenentHome from "./Pages/Tenent/TenentHome";
// import Admin_Profile from "./Pages/admin/AdminProfile";

const APPRouter = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<User_Layout />}>
          <Route index element={<User_Home />} />
          <Route path="login" element={<User_Login />} />
          <Route path="register" element={<User_Register />} />
        </Route>
        <Route path="/user" element={<User_layout2 />}>
          <Route index element={<User_Home />} />
          <Route path="upload/:long/:lat" element={<User_upload />} />
          <Route path="profile" element={<User_profile />} />
          <Route path="about" element={<User_about />} />
          <Route path="service" element={<User_services />} />
          <Route path="contact" element={<User_contact />} />
        </Route>

        <Route path="/admin" element={<Admin_layout />}>
          <Route index element={<Admin_Login />} />
          <Route path="adminRegister" element={<Admin_Register />} />
          <Route path="home" element={<AdminHomePage />} />
          <Route path="user" element={<AdminUser />} />
          <Route path="noti" element={<AdminNoti />} />
          <Route path="images" element={<AdminImages />} />
        </Route>

        <Route path="/tenent" element={<TenentLayout />}>
          <Route index element={<Tenent_Register />} />
          <Route path="register" element={<Tenent_Register />} />
          <Route path="login" element={<Tenent_Login />} />
        </Route>

        <Route path="/tenentAccepted" element={<TenentLoginUserLayout />}>
          <Route index element={<TenentHome />} />
          <Route path="home" element={<TenentHome />} />
          {/* <Route path="register" element={<Tenent_Register />} />
          <Route path="login" element={<Tenent_Login />} /> */}
        </Route>

        <Route path="*" element={<h1>Not Found</h1>} />
      </Routes>
    </Router>
  );
};

export default APPRouter;
