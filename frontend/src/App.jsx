import { useMemo, useRef, useState } from "react";
import {
  ArrowDownToLine, ArrowRight, BriefcaseBusiness, Check, CheckCircle2,
  CircleHelp, FileText, Gauge, LoaderCircle, LockKeyhole, RotateCcw,
  Sparkles, UploadCloud, X,
} from "lucide-react";

const categories = {
  technical_skills: "Technical skills",
  soft_skills: "People skills",
  experience_requirements: "Experience",
  responsibilities: "Responsibilities",
};

const ANALYSIS_TIMEOUT_MS = 5 * 60 * 1000;

function App() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const inputRef = useRef(null);

  const grouped = useMemo(() => {
    if (!analysis) return {};
    return analysis.results.reduce((groups, result) => {
      (groups[result.category] ||= []).push(result);
      return groups;
    }, {});
  }, [analysis]);

  function acceptFile(candidate) {
    if (!candidate) return;
    if (candidate.type !== "application/pdf" && !candidate.name.toLowerCase().endsWith(".pdf")) {
      setError("Please choose a PDF file.");
      return;
    }
    if (candidate.size > 10 * 1024 * 1024) {
      setError("Your PDF must be smaller than 10 MB.");
      return;
    }
    setFile(candidate);
    setError("");
  }

  async function analyze() {
    setError("");
    if (!file) return setError("Add your resume PDF to get started.");
    if (!jobDescription.trim()) return setError("Paste the job description to continue.");
    setLoading(true);
    setAnalysis(null);
    const body = new FormData();
    body.append("resume", file);
    body.append("job_description", jobDescription);
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), ANALYSIS_TIMEOUT_MS);
    try {
      const apiBase = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
      const response = await fetch(`${apiBase}/api/analyze`, {
        method: "POST",
        body,
        signal: controller.signal,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Analysis could not be completed.");
      setAnalysis(data);
      window.setTimeout(() => document.getElementById("results")?.scrollIntoView({ behavior: "smooth" }), 80);
    } catch (err) {
      if (err.name === "AbortError") {
        setError("Analysis is taking longer than five minutes. Please try again with a shorter job description or resume.");
      } else {
        setError(err.message || "Could not reach the analysis server. Check that the API is running.");
      }
    } finally {
      window.clearTimeout(timeoutId);
      setLoading(false);
    }
  }

  const supported = analysis?.results.filter((item) => item.status === "SUPPORTED").length || 0;
  const partial = analysis?.results.filter((item) => item.status === "PARTIAL").length || 0;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#top" aria-label="JobFit home"><span className="brand-icon"><BriefcaseBusiness size={19} /></span><span>jobfit<span className="brand-dot">.</span></span></a>
        <div className="sidebar-label">WORKSPACE</div>
        <a className="nav-link active" href="#analyzer"><Gauge size={17} /> Resume analyzer</a>
        <div className="sidebar-note"><div className="note-icon"><Sparkles size={16} /></div><strong>A clearer next step</strong><p>See where your experience meets the role, backed by evidence from your resume.</p></div>
        <div className="sidebar-bottom"><span className="avatar">JF</span><div><strong>JobFit workspace</strong><small>Resume insights</small></div><CircleHelp size={17} className="help" /></div>
      </aside>

      <main id="top" className="main-area">
        <header className="topbar"><div className="breadcrumb">Workspace <span>/</span> <strong>Resume analyzer</strong></div><div className="privacy"><LockKeyhole size={14} /> Your resume stays private</div></header>
        <div className="content" id="analyzer">
          <section className="intro"><div className="eyebrow"><span></span> YOUR NEXT OPPORTUNITY, IN FOCUS</div><h1>Find your fit.<br /><em>Own your next move.</em></h1><p className="intro-copy">Compare your experience with the role and get a clear, evidence-based view of where you stand.</p></section>

          <section className="form-grid" aria-label="Resume and job details">
            <article className="panel resume-panel">
              <div className="panel-heading"><div className="step">01</div><div><h2>Your resume</h2><p>Start with your most recent experience</p></div></div>
              <div className={`dropzone ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`} onDragOver={(e) => { e.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={(e) => { e.preventDefault(); setDragging(false); acceptFile(e.dataTransfer.files[0]); }} onClick={() => inputRef.current?.click()} role="button" tabIndex="0" onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}>
                <input ref={inputRef} type="file" accept="application/pdf,.pdf" hidden onChange={(e) => acceptFile(e.target.files[0])} />
                {file ? <><div className="file-icon"><FileText size={22} /></div><div className="file-info"><strong>{file.name}</strong><span>{(file.size / 1024 / 1024).toFixed(2)} MB · PDF document</span></div><button className="remove-file" aria-label="Remove resume" onClick={(e) => { e.stopPropagation(); setFile(null); }}><X size={17} /></button></> : <><div className="upload-icon"><UploadCloud size={22} /></div><div><strong>Drop your resume here</strong><span>or <b>browse files</b> from your device</span></div></>}
              </div>
              <div className="file-hint"><span>PDF only</span><span>Up to 10 MB</span><span>Text-based PDFs work best</span></div>
            </article>

            <article className="panel jd-panel">
              <div className="panel-heading"><div className="step">02</div><div><h2>The job description</h2><p>Paste the role you’re interested in</p></div></div>
              <textarea value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} maxLength={20000} placeholder="Paste the job description here..." aria-label="Job description" />
              <div className="character-count">{jobDescription.length.toLocaleString()} / 20,000 characters</div>
            </article>
          </section>

          <div className="action-row"><div className="reassurance"><LockKeyhole size={15} /><span>Files are used only to prepare your analysis.</span></div><button className="analyze-button" onClick={analyze} disabled={loading}>{loading ? <><LoaderCircle className="spin" size={17} /> Analyzing your fit...</> : <>Analyze my fit <ArrowRight size={17} /></>}</button></div>
          {error && <div className="error-banner" role="alert">{error}</div>}
          {loading && <div className="loading-card"><div className="loader-mark"><Sparkles size={20} /></div><div><strong>Putting the pieces together</strong><p>Reading your resume and comparing it with the role. Larger jobs may take a few minutes.</p></div><LoaderCircle className="spin loading-spinner" size={19} /></div>}

          {analysis && <section id="results" className="results-section">
            <div className="results-title"><div><div className="eyebrow"><span></span> YOUR MATCH REPORT</div><h2>A closer look at your fit</h2><p>Every match is grounded in evidence from the resume you shared.</p></div><button className="reset-button" onClick={() => { setAnalysis(null); setError(""); }}><RotateCcw size={15} /> New analysis</button></div>
            <div className="score-layout"><article className="score-card"><div className="score-top"><span>OVERALL MATCH</span><span className="score-spark"><Sparkles size={16} /></span></div><div className="score-number">{Number(analysis.score).toFixed(0)}<small>%</small></div><div className="score-track"><span style={{ width: `${Math.max(0, Math.min(100, analysis.score))}%` }} /></div><p>A useful signal to guide your next step, not a hiring decision.</p></article><div className="stat-card"><span className="stat-icon green"><Check size={17} /></span><div className="stat-number">{supported}</div><div className="stat-label">Strong matches</div><div className="stat-detail">Clearly supported by your resume</div></div><div className="stat-card"><span className="stat-icon amber"><Sparkles size={16} /></span><div className="stat-number">{partial}</div><div className="stat-label">Room to highlight</div><div className="stat-detail">Related experience found</div></div></div>
            <div className="report-heading"><h3>Requirement breakdown</h3><span>{analysis.results.length} items reviewed</span></div>
            <div className="category-list">{Object.entries(grouped).map(([key, items]) => <article className="category-card" key={key}><div className="category-heading"><div><span className="category-mark"><CheckCircle2 size={16} /></span><h4>{categories[key] || key}</h4></div><span>{items.filter((x) => x.status === "SUPPORTED").length}/{items.length} supported</span></div><div className="requirement-list">{items.map((item, index) => <details className="requirement" key={`${item.requirement}-${index}`}><summary><span className={`status-dot ${item.status.toLowerCase()}`} /><strong>{item.requirement}</strong><span className={`status-pill ${item.status.toLowerCase()}`}>{item.status === "SUPPORTED" ? "Strong match" : item.status === "PARTIAL" ? "Partial match" : "Not found"}</span><span className="chevron">⌄</span></summary><div className="requirement-detail"><p>{item.explanation}</p>{item.evidence && <div className="evidence"><span>RESUME EVIDENCE</span><p>{item.evidence}</p></div>}</div></details>)}</div></article>)}</div>
            <div className="report-footnote"><Sparkles size={16} /><span>Use these insights to tailor your application. A missing signal may mean the experience wasn’t stated clearly in your resume.</span></div>
          </section>}
          <footer className="page-footer"><span>JobFit <b>·</b> Make your experience count.</span><a href="mailto:support@jobfit.app">Need help?</a></footer>
        </div>
      </main>
    </div>
  );
}

export default App;
