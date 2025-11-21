import React from "react";

function Toast({ toast, onClose }) {
    if (!toast) return null;

    const bg =
        toast.type === "success"
            ? "#dcfce7"
            : toast.type === "error"
                ? "#fee2e2"
                : "#e5e7eb";

    const border =
        toast.type === "success"
            ? "#22c55e"
            : toast.type === "error"
                ? "#ef4444"
                : "#6b7280";

    return (
        <div
            style={{
                position: "fixed",
                right: 20,
                bottom: 20,
                maxWidth: 320,
                padding: "10px 14px",
                borderRadius: 10,
                background: bg,
                border: `1px solid ${border}`,
                boxShadow: "0 10px 25px rgba(15,23,42,0.2)",
                fontSize: 13,
                zIndex: 1000,
                display: "flex",
                gap: 8,
                alignItems: "center",
            }}
        >
            <div style={{ fontSize: 18 }}>
                {toast.type === "success" ? "✅" : toast.type === "error" ? "⚠️" : "ℹ️"}
            </div>
            <div style={{ flex: 1 }}>{toast.message}</div>
            <button
                onClick={onClose}
                style={{
                    border: "none",
                    background: "transparent",
                    cursor: "pointer",
                    fontSize: 16,
                    lineHeight: 1,
                    opacity: 0.6,
                }}
            >
                ×
            </button>
        </div>
    );
}

export default Toast;
