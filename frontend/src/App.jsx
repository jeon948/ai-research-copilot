import { useEffect, useRef, useState } from "react";
import axios from "axios";
import "./index.css";

const API_BASE_URL = "http://127.0.0.1:8000";

const studyTools = {
  summary: {
    label: "Summary",
    endpoint: "/summary",
    responseKey: "summary",
  },
  flashcards: {
    label: "Flashcards",
    endpoint: "/flashcards",
    responseKey: "flashcards",
  },
  quiz: {
    label: "Quiz",
    endpoint: "/quiz",
    responseKey: "quiz",
  },
  notes: {
    label: "Study Notes",
    endpoint: "/notes",
    responseKey: "notes",
  },
  importantQuestions: {
    label: "Important Questions",
    endpoint: "/important-questions",
    responseKey: "important_questions",
  },
  revisionSheet: {
    label: "Revision Sheet",
    endpoint: "/revision-sheet",
    responseKey: "revision_sheet",
  },
};

function App() {
  const [file, setFile] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [selectedTool, setSelectedTool] = useState("summary");
  const [toolResult, setToolResult] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [asking, setAsking] = useState(false);
  const [theme, setTheme] = useState("dark");
  const [notice, setNotice] = useState("");
  const chatEndRef = useRef(null);

  const activeDocument = documents.length > 0 ? documents[documents.length - 1] : null;

  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, asking]);

  const showNotice = (message) => {
    setNotice(message);
    setTimeout(() => setNotice(""), 3000);
  };

  const getErrorMessage = (err, fallback) => {
    return (
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      fallback
    );
  };

  const fetchDocuments = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/documents`);
      setDocuments(
        res.data.uploaded_documents ||
          res.data.documents ||
          res.data.files ||
          []
      );
    } catch (err) {
      console.error("Documents error:", err);
      showNotice("Failed to refresh PDFs");
    }
  };

  const uploadPDF = async () => {
    if (!file) {
      showNotice("Please select a PDF first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setUploading(true);

      const res = await axios.post(`${API_BASE_URL}/upload-pdf`, formData);

      showNotice(res.data.message || "PDF uploaded successfully");
      await fetchDocuments();
      setFile(null);
    } catch (err) {
      console.error("Upload error:", err);
      showNotice(getErrorMessage(err, "PDF upload failed"));
    } finally {
      setUploading(false);
    }
  };

  const deleteDocument = async (filename) => {
    const confirmDelete = window.confirm(
      `Are you sure you want to remove "${filename}"?`
    );

    if (!confirmDelete) return;

    try {
      setUploading(true);

      const res = await axios.delete(
        `${API_BASE_URL}/delete-document/${encodeURIComponent(filename)}`
      );

      setDocuments(res.data.uploaded_documents || []);
      showNotice(res.data.message || "Document deleted successfully");
    } catch (err) {
      console.error("Delete error:", err);
      showNotice(getErrorMessage(err, "Failed to delete document"));
    } finally {
      setUploading(false);
    }
  };

  const generateStudyTool = async () => {
    const tool = studyTools[selectedTool];

    try {
      setGenerating(true);
      setToolResult("");

      const res = await axios.get(`${API_BASE_URL}${tool.endpoint}`);

      setToolResult(
        res.data[tool.responseKey] ||
          res.data.response ||
          res.data.result ||
          JSON.stringify(res.data, null, 2)
      );

      showNotice(`${tool.label} generated successfully`);
    } catch (err) {
      console.error("Study tool error:", err);
      showNotice(getErrorMessage(err, "Failed to generate"));
    } finally {
      setGenerating(false);
    }
  };

  const askDocument = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      showNotice("Please enter a question");
      return;
    }

    const userMessage = {
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");

    try {
      setAsking(true);

      const res = await axios.get(`${API_BASE_URL}/ask-document`, {
        params: { question: trimmedQuestion },
      });

      const aiAnswer =
        res.data.answer ||
        res.data.response ||
        res.data.result ||
        JSON.stringify(res.data, null, 2);

      const assistantMessage = {
        role: "assistant",
        content: aiAnswer,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Ask error:", err);

      const errorMessage = {
        role: "assistant",
        content: getErrorMessage(err, "Failed to get answer"),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setAsking(false);
    }
  };

  const handleQuestionKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      askDocument();
    }
  };

  const clearChat = () => {
    setMessages([]);
    showNotice("Chat cleared");
  };

  const downloadTextFile = (content, filename) => {
    if (!content) {
      showNotice("Generate something first");
      return;
    }

    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();

    URL.revokeObjectURL(url);
  };

  const downloadChat = () => {
    if (messages.length === 0) {
      showNotice("No chat to download");
      return;
    }

    const chatText = messages
      .map((msg) => `${msg.role === "user" ? "You" : "AI"}:\n${msg.content}`)
      .join("\n\n----------------------\n\n");

    downloadTextFile(chatText, "ai-copilot-chat.txt");
  };

  return (
    <div className={`app ${theme}`}>
      {notice && <div className="notice-toast">{notice}</div>}

      <aside className="document-panel">
        <div className="brand">
          <div className="logo">ARC</div>
          <div>
            <h2>AI Research Copilot</h2>
            <p>Document intelligence workspace</p>
          </div>
        </div>

        <div className="panel-section">
          <div className="section-title">
            <span>Uploaded PDFs</span>
            <button onClick={fetchDocuments} disabled={uploading}>
              Refresh
            </button>
          </div>

          {documents.length === 0 ? (
            <div className="empty-docs">
              <p>No PDFs uploaded yet.</p>
              <span>Upload a PDF from the workspace.</span>
            </div>
          ) : (
            <div className="document-list">
              {documents.map((doc, index) => (
                <div
                  className={`document-card ${
                    doc === activeDocument ? "active-document-card" : ""
                  }`}
                  key={index}
                >
                  <div className="doc-info">
                    <div className="doc-badge">PDF</div>
                    <span>{doc}</span>
                  </div>

                  <button
                    className="delete-btn"
                    onClick={() => deleteDocument(doc)}
                    disabled={uploading}
                  >
                    X
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="sidebar-note">
          <p>Active Document</p>
          <span>{activeDocument || "No active document yet."}</span>
        </div>
      </aside>

      <main className="workspace-panel">
        <header className="workspace-header">
          <div>
            <p className="eyebrow">Study Workspace</p>
            <h1>Generate study materials from any PDF</h1>
            <p>
              Upload a PDF, choose a tool, and generate summaries, flashcards,
              quizzes, notes, or revision sheets.
            </p>
          </div>

          <button
            className="theme-toggle"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? "Light Mode" : "Dark Mode"}
          </button>
        </header>

        <section className="upload-card">
          <div>
            <h2>Upload PDF</h2>
            <p>Use class notes, resumes, reports, offer letters, or papers.</p>
          </div>

          <label className="upload-zone">
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files[0])}
            />

            <div className="upload-icon">PDF</div>
            <h3>{file ? file.name : "Choose a PDF"}</h3>
            <p>
              {file
                ? "PDF selected. Click upload to index it."
                : "Click here to browse your file."}
            </p>
          </label>

          <button
            className="primary-btn"
            onClick={uploadPDF}
            disabled={uploading}
          >
            {uploading ? "Processing..." : "Upload and Index"}
          </button>
        </section>

        <section className="tool-card">
          <div className="tool-card-header">
            <div>
              <h2>Study Tool Generator</h2>
              <p>Select what you want AI to create from the uploaded PDF.</p>
            </div>
          </div>

          <div className="tool-controls">
            <select
              value={selectedTool}
              onChange={(e) => setSelectedTool(e.target.value)}
            >
              {Object.entries(studyTools).map(([key, tool]) => (
                <option key={key} value={key}>
                  {tool.label}
                </option>
              ))}
            </select>

            <button
              className="primary-btn"
              onClick={generateStudyTool}
              disabled={generating}
            >
              {generating ? "Generating..." : "Generate"}
            </button>
          </div>

          <div className="result-area">
            {toolResult ? (
              <>
                <div className="result-header">
                  <p>{studyTools[selectedTool].label} Output</p>

                  <button
                    className="download-btn"
                    onClick={() =>
                      downloadTextFile(
                        toolResult,
                        `${studyTools[selectedTool].label
                          .toLowerCase()
                          .replaceAll(" ", "-")}.txt`
                      )
                    }
                  >
                    Download
                  </button>
                </div>

                <div className="result-box">{toolResult}</div>
              </>
            ) : (
              <div className="placeholder-result">
                <p>
                  {generating
                    ? "Generating your study material..."
                    : "Your generated result will appear here."}
                </p>
              </div>
            )}
          </div>
        </section>
      </main>

      <aside className="copilot-panel">
        <div className="copilot-header">
          <div>
            <p className="eyebrow">Ask AI</p>
            <h2>Document Copilot</h2>
            <p className="active-doc-text">
              {activeDocument
                ? `Chatting with: ${activeDocument}`
                : "Upload a PDF to start chatting"}
            </p>
          </div>

          <div className="status-dot">
            <span></span>
            Active
          </div>
        </div>

        <div className="copilot-actions">
          <button onClick={clearChat} disabled={messages.length === 0}>
            Clear
          </button>
          <button onClick={downloadChat} disabled={messages.length === 0}>
            Export
          </button>
        </div>

        <div className="copilot-answer">
          {messages.length === 0 ? (
            <div className="empty-chat">
              <p>Ask anything about your uploaded PDF.</p>
              <span>
                Works for resumes, academic notes, reports, offer letters, and
                research papers.
              </span>
            </div>
          ) : (
            <div className="chat-messages">
              {messages.map((msg, index) => (
                <div
                  className={`chat-message ${
                    msg.role === "user" ? "user-message" : "assistant-message"
                  }`}
                  key={index}
                >
                  <div className="message-label">
                    {msg.role === "user" ? "You" : "AI Copilot"}
                  </div>
                  <div className="message-bubble">{msg.content}</div>
                </div>
              ))}

              {asking && (
                <div className="chat-message assistant-message">
                  <div className="message-label">AI Copilot</div>
                  <div className="message-bubble">Thinking...</div>
                </div>
              )}

              <div ref={chatEndRef}></div>
            </div>
          )}
        </div>

        <div className="copilot-input">
          <textarea
            placeholder="Ask about your document..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleQuestionKeyDown}
          />

          <button onClick={askDocument} disabled={asking}>
            {asking ? "Thinking..." : "Ask AI"}
          </button>
        </div>
      </aside>
    </div>
  );
}

export default App;