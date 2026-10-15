import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../api";

function VerifyOtp() {
  const location = useLocation();
  const navigate = useNavigate();
  const [email] = useState(location.state?.email || "");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleVerify = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/verify-otp", { email, otp });
      setMessage("Verified! Redirecting to login...");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setError(err.response?.data?.detail || "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setError("");
    setMessage("");
    try {
      await api.post("/resend-otp", { email });
      setMessage("A new code has been sent to your email");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not resend code");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Verify your email</h2>
        <p className="subtitle">We sent a 6-digit code to <strong>{email}</strong></p>
        <form onSubmit={handleVerify}>
          <div className="form-group">
            <label>Verification code</label>
            <input
              type="text"
              maxLength={6}
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              required
            />
          </div>
          {error && <p className="error-text">{error}</p>}
          {message && <p className="success-text">{message}</p>}
          <button type="submit" disabled={loading}>{loading ? "Verifying..." : "Verify"}</button>
        </form>
        <p className="switch-link">
          Didn't get a code? <button className="link-btn" onClick={handleResend}>Resend</button>
        </p>
      </div>
    </div>
  );
}

export default VerifyOtp;