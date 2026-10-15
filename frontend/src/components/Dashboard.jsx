import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FileText, Upload, LogOut, Sparkles, Building2, ExternalLink, MapPin, Briefcase, GraduationCap, IndianRupee, Trash2 } from "lucide-react";
import toast from "react-hot-toast";
import api from "../api";

function Dashboard() {
  const [user, setUser] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [matches, setMatches] = useState(null);
  const [matchingId, setMatchingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const navigate = useNavigate();

  const loadData = async () => {
    try {
      const [meRes, resumesRes] = await Promise.all([api.get("/me"), api.get("/resumes")]);
      setUser(meRes.data);
      setResumes(resumesRes.data);
    } catch (err) {
      navigate("/login");
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post("/resumes/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success("Resume uploaded");
      setFile(null);
      await loadData();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleMatch = async (resumeId) => {
    setMatchingId(resumeId);
    setMatches(null);
    try {
      const res = await api.post(`/resumes/${resumeId}/match`);
      setMatches(res.data.matches);
      toast.success(`Found ${res.data.matches.length} matches`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Matching failed");
    } finally {
      setMatchingId(null);
    }
  };

  const handleDelete = async (resumeId) => {
    if (!window.confirm("Delete this resume? This can't be undone.")) return;
    setDeletingId(resumeId);
    try {
      await api.delete(`/resumes/${resumeId}`);
      toast.success("Resume deleted");
      if (matches) setMatches(null);
      await loadData();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Delete failed");
    } finally {
      setDeletingId(null);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const scoreClass = (score) => {
    if (score >= 0.6) return "score-high";
    if (score >= 0.4) return "score-mid";
    return "score-low";
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="brand"><Sparkles size={20} /> Resume Matcher</div>
        <div className="header-right">
          {user && <span className="user-email">{user.email}</span>}
          <button className="logout-btn" onClick={handleLogout}>
            <LogOut size={16} /> Logout
          </button>
        </div>
      </header>

      <div className="dashboard-content">
        <section className="card">
          <h3><Upload size={18} /> Upload a resume</h3>
          <form onSubmit={handleUpload} className="upload-form">
            <input type="file" accept=".pdf,.docx" onChange={(e) => setFile(e.target.files[0])} />
            <button type="submit" disabled={!file || uploading}>
              {uploading ? "Uploading..." : "Upload"}
            </button>
          </form>
        </section>

        <section className="card">
          <h3><FileText size={18} /> Your resumes</h3>
          {resumes.length === 0 ? (
            <p className="empty-state">No resumes uploaded yet — add one above to get started.</p>
          ) : (
            <ul className="resume-list">
              {resumes.map((r) => (
                <li key={r.id} className="resume-item">
                  <span className="resume-name"><FileText size={16} className="file-icon" /> {r.filename}</span>
                  <div className="resume-actions">
                    <button
                      className="match-btn"
                      onClick={() => handleMatch(r.id)}
                      disabled={matchingId === r.id}
                    >
                      {matchingId === r.id ? "Matching..." : "Find matching jobs"}
                    </button>
                    <button
                      className="delete-btn"
                      onClick={() => handleDelete(r.id)}
                      disabled={deletingId === r.id}
                      title="Delete resume"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>

        {matches && (
          <section className="card">
            <h3><Building2 size={18} /> Match results <span className="match-count">{matches.length}</span></h3>
            <div className="match-grid">
              {matches.map((m) => (
                <div key={m.job_id} className="match-card">
                  <div className="match-card-header">
                    <div>
                      <h4>{m.title}</h4>
                      <span className="company">{m.company}</span>
                    </div>
                    <span className={`score-badge ${scoreClass(m.score)}`}>
                      {Math.round(m.score * 100)}%
                    </span>
                  </div>

                  <div className="match-meta">
                    {m.location && <span className="meta-tag"><MapPin size={13} /> {m.location}</span>}
                    {m.work_type && <span className="meta-tag"><Briefcase size={13} /> {m.work_type}</span>}
                    {m.experience_level && <span className="meta-tag"><GraduationCap size={13} /> {m.experience_level}</span>}
                    {(m.salary_min || m.salary_max) && (
                      <span className="meta-tag">
                        <IndianRupee size={13} />
                        {m.salary_min ? Math.round(m.salary_min).toLocaleString() : "?"}
                        {" - "}
                        {m.salary_max ? Math.round(m.salary_max).toLocaleString() : "?"}
                      </span>
                    )}
                  </div>

                  <p className="match-description">{m.description}</p>

                  {m.url ? (
                    <a href={m.url} target="_blank" rel="noopener noreferrer" className="apply-btn">
                      Apply Now <ExternalLink size={14} />
                    </a>
                  ) : (
                    <span className="no-link">No application link available</span>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

export default Dashboard;