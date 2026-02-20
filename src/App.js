import React, { useState, useRef } from "react";
import * as pdfjsLib from "pdfjs-dist";
import "./App.css";

pdfjsLib.GlobalWorkerOptions.workerSrc =
  `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

function App() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! I am Banking AI Assistant. Ask your queries." }
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef();

  // =============================
  // 🔥 CALL BACKEND API
  // =============================
  const callAPI = async (text) => {
    try {
      setLoading(true); 

      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          customer_query: text   // ✅ Must match FastAPI model
        })
      });

      if (!response.ok) {
        throw new Error("Server Error");
      }

      const data = await response.json();

      // ✅ JSX formatted response (NOT paragraph string)
      const formattedResponse = (
        <div>
          <p><strong>📌 Ticket:</strong> {data.ticket_title}</p>
          <p><strong>📂 Category:</strong> {data.complaint_type} → {data.sub_category}</p>
          <p><strong>⚡ Priority:</strong> {data.priority}</p>
          <p><strong>📊 Risk Score:</strong> {data.risk_score}</p>
          <p><strong>🚨 Risk Level:</strong> {data.risk_level}</p>
          <p><strong>😊 Sentiment:</strong> {data.sentiment}</p>
          <p><strong>⏱ SLA:</strong> {data.SLA_hours} hrs</p>

          <p><strong>📝 Summary:</strong></p>
          <p>{data.summary}</p>

          <p><strong>🛠 Resolution Steps:</strong></p>
          <ul>
            {data.resolution_steps?.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ul>

          <p><strong>💬 Agent Reply:</strong></p>
          <p>{data.agent_reply}</p>
        </div>
      );

      setMessages(prev => [
        ...prev,
        { sender: "bot", text: formattedResponse }
      ]);

    } catch (error) {
      console.error("API Error:", error);
      setMessages(prev => [
        ...prev,
        { sender: "bot", text: "❌ Unable to connect to Banking AI Engine." }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // =============================
  // 📩 HANDLE TEXT MESSAGE
  // =============================
  const handleSend = () => {
    if (!input.trim()) return;

    setMessages(prev => [...prev, { sender: "user", text: input }]);

    callAPI(input);
    setInput("");
  };

  // =============================
  // 📄 HANDLE PDF UPLOAD
  // =============================
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setMessages(prev => [
      ...prev,
      { sender: "user", text: `📄 Uploaded: ${file.name}` }
    ]);

    const fileReader = new FileReader();

    fileReader.onload = async function () {
      const typedarray = new Uint8Array(this.result);
      const pdf = await pdfjsLib.getDocument(typedarray).promise;

      let extractedText = "";

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        extractedText += textContent.items.map(item => item.str).join(" ");
      }

      callAPI(extractedText);
    };

    fileReader.readAsArrayBuffer(file);
  };

  // =============================
  // 🖥 UI
  // =============================
  return (
    <div className="chat-container">

      <div className="chat-header">
        🏦 AI Powered Banking Customer Query Summarizer
      </div>

      <div className="chat-body">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-bubble ${msg.sender}`}>
            {typeof msg.text === "string"
              ? msg.text
              : msg.text}
          </div>
        ))}

        {loading && (
          <div className="chat-bubble bot">
            ⏳ Analyzing complaint...
          </div>
        )}
      </div>

      <div className="chat-input">

        <button
          className="file-btn"
          onClick={() => fileInputRef.current.click()}
        >
          📎
        </button>

        <input
          type="file"
          accept="application/pdf"
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={handleFileUpload}
        />

        <input
          type="text"
          placeholder="Describe your banking issue..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />

        <button onClick={handleSend}>Send</button>
      </div>

    </div>
  );
}

export default App;