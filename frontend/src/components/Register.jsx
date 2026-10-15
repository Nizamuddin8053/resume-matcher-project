import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Mail, Lock, UserPlus } from "lucide-react";
import toast from "react-hot-toast";
import api from "../api";

function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.post("/signup", { email, password });
      toast.success("Account created! Check your email for a verification code.");
      navigate("/verify-otp", { state: { email } });
    } catch (err) {
      const detail = err.response?.data?.detail;
      const message = Array.isArray(detail) ? detail.map((d) => d.msg).join(", ") : detail || "Something went wrong";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-icon"><UserPlus size={26} /></div>
        <h2>Create your account</h2>
        <p className="subtitle">Start matching your resume to real jobs</p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label><Mail size={14} /> Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label><Lock size={14} /> Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            <span className="hint">Min 8 characters, 1 uppercase, 1 number, 1 special character</span>
          </div>
          <button type="submit" disabled={loading}>
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>
        <p className="switch-link">Already have an account? <a href="/login">Login</a></p>
      </div>
    </div>
  );
}

export default Register;