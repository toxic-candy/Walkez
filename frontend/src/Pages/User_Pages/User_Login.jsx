import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import "../../CSS/User_Css/Login.css";
import { store_cookies_data } from "../../Utility/Auth";
import GoogleButton from "./Components/GoogleButton";
import Loader from "./Components/Loader";

const User_Login = () => {
  const navigate = useNavigate();
  const [user_email, setUser_email] = useState("");
  const [user_password, setUser_password] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const login = async (e) => {
    e.preventDefault();
    setLoading(true);
    const apiUrl = import.meta.env.VITE_REACT_APP_URL;
    const options = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_email: user_email,
        user_password: user_password,
      }),
    };

    const response = await fetch(`${apiUrl}/user_route/login`, options);
    const data = await response.json();
    if (response.status === 200) {
      console.log(data);
      store_cookies_data(data.refresh_token, data.access_token);
      toast.success(data.message);
      setUser_email("");
      setUser_password("");
      navigate("/");
    } else {
      toast.error(data.message);
    }
    setLoading(false);
  };

  return (
    <div className="body1 mr-[-2%] ">
      {loading ? (
        <div className="bg-[rgba(32,13,13,0.27)] w-[200%] h-[100vh] justify-center items-center flex mr-[-20%]">
          <Loader />
        </div>
      ) : (
        <div className=" flex justify-center items-center h-screen xs:block xs:ml-[5%] xs:mt-20">
          <div className="login_container xs:w-[95%]">
            <h1 className="name">
            Walkez <img src="" alt="" />
            </h1>
            <h2 className="login">LOGIN</h2>
            <form className="login_form" method="post" onSubmit={login}>
              <input
                type="text"
                placeholder="User email"
                required
                className="inputtxt xs:w-[90%] w-[75%]"
                value={user_email}
                onChange={(e) => setUser_email(e.target.value)}
              />
              <br />
              <input
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                required
                className="inputtxt xs:w-[90%] w-[75%]"
                value={user_password}
                onChange={(e) => setUser_password(e.target.value)}
              />
              <div className="showPassword">
                <input
                  type="checkbox"
                  id="showPassword"
                  checked={showPassword}
                  onChange={() => setShowPassword(!showPassword)}
                />{" "}
                Show Password
              </div>
              <div className=" flex justify-center flex-col align-middle w-[100%] ">
                <input
                  type="submit"
                  className="submit1  w-[75%] m-auto xs:w-[90%]"
                  value="Login"
                />
              </div>
              <GoogleButton isLogin={true} />
            </form>
            <p className="signup_link">
              <Link to={`/register`} className="link1">
                Don't have an account Sign up
              </Link>
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default User_Login;
