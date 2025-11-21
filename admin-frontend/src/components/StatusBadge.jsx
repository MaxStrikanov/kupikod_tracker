import React from "react";

function StatusBadge({ status }) {
    let bg = "#e5e7eb";
    let color = "#374151";
    let text = status;

    if (status === "ok") {
        bg = "#dcfce7";
        color = "#166534";
        text = "ТЗ выполнено";
    } else if (status === "minor_issues") {
        bg = "#fef9c3";
        color = "#854d0e";
        text = "Незначительные замечания";
    } else if (status === "fail") {
        bg = "#fee2e2";
        color = "#b91c1c";
        text = "ТЗ не выполнено";
    }

    return (
        <span
            style={{
                padding: "2px 8px",
                borderRadius: 999,
                fontSize: 11,
                background: bg,
                color,
                border: "1px solid rgba(0,0,0,0.05)",
            }}
        >
            {text}
        </span>
    );
}

export default StatusBadge;
