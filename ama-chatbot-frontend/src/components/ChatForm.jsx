import { useState } from "react";

export default function ChatForm() {
    const [query, setQuery] = useState("");
    const [response, setResponse] = useState("");
    const [editableResponse, setEditableResponse] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setResponse("");
        setEditableResponse("");

        try {
            const res = await fetch("http://127.0.0.1:8000/generate-reply", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query }),
            });

            const data = await res.json();
            const replyText = data?.reply?.result ?? "No response received";
            setResponse(replyText);
            setEditableResponse(replyText);
        } catch (err) {
            setResponse("Fehler beim Abrufen der Antwort.");
        }

        setLoading(false);
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h2 style={styles.heading}>📩 AMA Email Reply Generator</h2>
                <form onSubmit={handleSubmit}>
                    <textarea
                        rows={8}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Füge hier deine erhaltene E-Mail ein..."
                        required
                        disabled={loading}
                        style={styles.textarea}
                    />
                    <button type="submit" disabled={loading} style={styles.button}>
                        {loading ? "Generiere Antwort..." : "Antwort generieren"}
                    </button>
                </form>

                {editableResponse && (
                    <div style={styles.responseSection}>
                        <h3 style={styles.subheading}>✉️ Generierte Antwort (bearbeitbar):</h3>
                        <textarea
                            rows={10}
                            value={editableResponse}
                            onChange={(e) => setEditableResponse(e.target.value)}
                            style={styles.textarea}
                        />
                    </div>
                )}
            </div>
        </div>
    );
}

const styles = {
    container: {
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        backgroundColor: "#f2f4f8",
        padding: "2rem",
    },
    card: {
        width: "100%",
        maxWidth: "700px",
        backgroundColor: "#ffffff",
        borderRadius: "12px",
        boxShadow: "0 4px 20px rgba(0, 0, 0, 0.1)",
        padding: "2rem",
    },
    heading: {
        textAlign: "center",
        marginBottom: "1.5rem",
        fontSize: "1.5rem",
        color: "#333",
    },
    subheading: {
        fontSize: "1.1rem",
        marginBottom: "0.5rem",
        color: "#444",
    },
    textarea: {
        width: "100%",
        padding: "0.75rem",
        fontSize: "1rem",
        borderRadius: "8px",
        border: "1px solid #ccc",
        marginBottom: "1rem",
        resize: "vertical",
        boxShadow: "inset 0 1px 3px rgba(0,0,0,0.05)",
    },
    button: {
        display: "block",
        width: "100%",
        padding: "0.75rem",
        fontSize: "1rem",
        backgroundColor: "#4f46e5",
        color: "#ffffff",
        border: "none",
        borderRadius: "8px",
        cursor: "pointer",
        transition: "background-color 0.3s ease",
    },
    responseSection: {
        marginTop: "2rem",
    },
};
